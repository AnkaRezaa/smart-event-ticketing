import json
import os
import time
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import User
from app.security.session import get_current_user_from_session
from app.schemas.schemas import CVLabInspectRequest
from app.cv.image_loader import decode_base64_image
from app.cv.face_detector import face_detector
from app.cv.quality_check import validate_face_quality
from app.cv.preprocessing import preprocess_face
from app.cv.hog_extractor import hog_extractor
from app.cv.visualization import generate_pipeline_visualizations
from app.ml.inference import inference_engine
from app.ml.model_manager import model_manager
from app.config import settings

router = APIRouter(tags=["cv_lab"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/cv-lab", response_class=HTMLResponse)
def cv_lab_page(request: Request):
    user = get_current_user_from_session(request)
    return templates.TemplateResponse(
        request=request,
        name="cv_lab/index.html",
        context={"current_user": user}
    )

@router.get("/research/results", response_class=HTMLResponse)
def research_results_page(request: Request):
    user = get_current_user_from_session(request)
    report_path = os.path.join(str(settings.BASE_DIR), "research", "results", "experiment_report.json")
    report_data = None
    raw_json = "{}"
    if os.path.exists(report_path):
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                report_data = json.load(f)
                raw_json = json.dumps(report_data, indent=2)
        except Exception:
            pass

    return templates.TemplateResponse(
        request=request,
        name="cv_lab/experiments.html",
        context={
            "current_user": user,
            "report": report_data,
            "raw_json": raw_json
        }
    )

@router.post("/api/cv-lab/inspect")
def inspect_image_api(req: CVLabInspectRequest, db: Session = Depends(get_db)):
    start_time = time.time()

    # Step 1: Decode
    image, err = decode_base64_image(req.image_base64)
    if image is None:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": f"Failed to decode image: {err}"}
        )

    # Step 2: Detect faces
    boxes = face_detector.detect_faces(image)
    if len(boxes) == 0:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "No face detected in the image. Please face the camera directly."}
        )

    # Step 3: Compute complete visualization maps
    vis_dict = generate_pipeline_visualizations(image, boxes[0])

    # Step 4: ML Prediction if gallery is populated
    inference_engine.refresh_model()
    ml_decision = None
    if inference_engine.knn.is_fitted():
        roi = face_detector.extract_face_roi(image, boxes[0])
        preprocessed = preprocess_face(roi)
        feats, _ = hog_extractor.extract_features(preprocessed)
        knn_res = inference_engine.knn.predict_with_distances(feats)

        user_obj = None
        if knn_res["predicted_label"]:
            user_obj = db.query(User).filter(User.id == knn_res["predicted_label"]).first()

        within_threshold = (knn_res["min_distance"] <= inference_engine.active_threshold)

        ml_decision = {
            "predicted_user_id": knn_res["predicted_label"],
            "predicted_label": user_obj.name if user_obj else knn_res["predicted_label"],
            "min_distance": float(round(knn_res["min_distance"], 4)),
            "active_threshold": float(inference_engine.active_threshold),
            "is_within_threshold": within_threshold,
            "confidence": float(round(knn_res["confidence_score"], 4))
        }

    latency_ms = (time.time() - start_time) * 1000

    return JSONResponse(content={
        "success": True,
        "latency_ms": latency_ms,
        "visualizations": vis_dict,
        "ml_decision": ml_decision
    })

