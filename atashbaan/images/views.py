from base64 import b64decode
from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.files.base import ContentFile
from django.core.paginator import InvalidPage
from django.db.models.query import QuerySet
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseNotFound,
    HttpResponseRedirect,
)
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import CreateView, DeleteView, DetailView, ListView
from django.views.generic.base import ContextMixin, View

from atashbaan.images.forms import ImageUploadForm, SaveProcessedImageForm
from atashbaan.images.image_processor import fire_recognizer
from atashbaan.images.models import Image


# Create your views here.
class ImageUploadView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = "images/image_upload.html"
    form_class = ImageUploadForm
    success_message = "تصویر با موفقیت بارگذاری شد."
    success_url = "/images/process/"

    def form_valid(self, form: Any) -> HttpResponse:
        form.instance.user = self.request.user
        form.instance.tag = "unprocessed"
        image = form.save(commit=False)
        image.save()

        return super().form_valid(form)


image_upload_view = ImageUploadView.as_view()


class ImageProcessView(LoginRequiredMixin, ContextMixin, View):
    template_name = "images/image_process.html"
    success_message = "تصویر پردازش شده با موفقیت ذخیره شد."
    save_form = SaveProcessedImageForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        user = self.request.user
        form = self.save_form()

        self.extra_context = {"user": user, "form": form}

        return super().get_context_data(**kwargs)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        context = self.get_context_data()
        qd_image_pk = self.request.GET.get("image-pk")

        if qd_image_pk:
            try:
                img = Image.unprocessed.get(pk=qd_image_pk)
            except Image.DoesNotExist:
                return HttpResponseNotFound(render(request, "404.html"))
        else:
            try:
                img = Image.unprocessed.filter(user=context["user"]).latest(
                    "created_at"
                )
            except Image.DoesNotExist:
                return HttpResponseNotFound(render(request, "404.html"))

        if img.user == self.request.user:
            img_fp = img.image.path

            image = fire_recognizer(img_fp)

            context["form"].fields["image"].initial = image

            return render(request, self.template_name, context)
        else:
            return HttpResponseForbidden(render(request, "403.html"))

    def post(self, request, *args, **kwargs):
        user = self.request.user
        form = self.save_form(request.POST or None)
        qd_image_pk = self.request.GET.get("image-pk")

        if qd_image_pk:
            try:
                usr_image = user.images.get(pk=qd_image_pk)
            except Image.DoesNotExist:
                return HttpResponseNotFound(render(request, "404.html"))
        else:
            try:
                usr_image = user.images.latest("created_at")
            except Image.DoesNotExist:
                return HttpResponseNotFound(render(request, "404.html"))

        # file naming
        usr_image_name = usr_image.image.name
        full_file_name = usr_image_name.split("/")[-1]
        file_name = full_file_name.split(".")[0]
        ext = usr_image_name.split(".", 1)[1]

        if form.is_valid():
            img = form.cleaned_data["image"]

            image_file = ContentFile(
                b64decode(img), name=file_name + "-processed." + ext
            )

            image = Image(image=image_file)
            image.tag = "processed"
            image.user = self.request.user
            image.save()

            messages.success(self.request, self.success_message)
        else:
            context = self.get_context_data()
            context.update({"form": form})

            return render(request, self.template_name, context=context)

        return HttpResponseRedirect(reverse("images:image_list"))


image_process_view = ImageProcessView.as_view()


class ImageListView(LoginRequiredMixin, ListView):
    template_name = "images/image_list.html"
    model = Image
    paginate_by = 5
    paginate_orphans = 1
    context_object_name = "images"

    def get_queryset(self) -> QuerySet[Any]:
        queryset = Image.processed.filter(user=self.request.user)

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        del context["object_list"]

        user = self.request.user

        unprocessed_images = Image.unprocessed.filter(user=self.request.user)
        unprocessed_page_size = self.get_paginate_by(unprocessed_images)
        if unprocessed_page_size:
            (
                unprocessed_paginator,
                unprocessed_page,
                unprocessed_images,
                unprocessed_is_paginated,
            ) = self.custom_paginate_queryset(unprocessed_images, unprocessed_page_size)
            context.update(
                {
                    "unprocessed_paginator": unprocessed_paginator,
                    "unprocessed_page_obj": unprocessed_page,
                    "unprocessed_is_paginated": unprocessed_is_paginated,
                    "unprocessed_images": unprocessed_images,
                    "user": user,
                }
            )
        else:
            context.update(
                {
                    "unprocessed_paginator": None,
                    "unprocessed_page_obj": None,
                    "unprocessed_is_paginated": False,
                    "unprocessed_images": unprocessed_images,
                    "user": user,
                }
            )

        return context

    def custom_paginate_queryset(self, queryset, page_size):
        paginator = self.get_paginator(
            queryset,
            page_size,
            orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty(),
        )
        page_kwarg = "unprocessed-image-page"
        page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
        try:
            page_number = int(page)
        except ValueError:
            if page == "last":
                page_number = paginator.num_pages
            else:
                raise Http404(
                    _("Page is not “last”, nor can it be converted to an int.")
                )
        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())
        except InvalidPage as e:
            raise Http404(
                _("Invalid page (%(page_number)s): %(message)s")
                % {"page_number": page_number, "message": str(e)}
            )


image_list_view = ImageListView.as_view()


class ImageDetailView(LoginRequiredMixin, DetailView):
    template_name = "images/image_detail.html"
    model = Image
    context_object_name = "image"

    def get_queryset(self) -> QuerySet[Any]:
        queryset = Image.objects.filter(user=self.request.user)

        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        del context["object"]

        return context


image_detail_view = ImageDetailView.as_view()


class ImageDeleteView(DeleteView):
    model = Image
    context_object_name = "image"
    success_url = reverse_lazy("images:image_list")

    def form_valid(self, form):
        messages.success(self.request, "تصویر مورد نظر با موفقیت حذف شد.")

        return super().form_valid(form)


image_delete_view = ImageDeleteView.as_view()
