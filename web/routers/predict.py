from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from web.core.dependencies import require_user
from web.services.predict_service import get_attributes, predict

router = APIRouter(prefix="/predict", tags=["Predict"])
templates = Jinja2Templates(directory="web/templates")


@router.get("/", response_class=HTMLResponse)
async def predict_page(request: Request, user=Depends(require_user)):
    attributes = get_attributes()

    return templates.TemplateResponse(
        request,
        "predict.html",
        {
            "user": user.username,
            "attributes": attributes,
        },
    )


@router.post("/", response_class=HTMLResponse)
async def predict_submit(
    request: Request,
    user=Depends(require_user),
):
    form = await request.form()
    form_data = dict(form)
    print(form_data)

    prediction = predict([form_data])
    print(prediction)

    return templates.TemplateResponse(
        request,
        "predict.html",
        {
            "user": user.username,
            "attributes": get_attributes(),
            "prediction": prediction,
        },
    )