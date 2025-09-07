from fastapi import APIRouter, Depends, HTTPException
from . import views

router = APIRouter()

router.add_api_route("/post/{hashpath}", views.post_detail_view, methods=["GET"])
router.add_api_route("/folder/{hashpath}", views.folder_detail_view, methods=["GET"])
router.add_api_route("/profiles", views.profile_list_view, methods=["GET"])
router.add_api_route("/{folder}/{filename}", views.serve_image, methods=["GET"])
