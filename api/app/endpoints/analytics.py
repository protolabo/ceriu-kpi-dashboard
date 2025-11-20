from fastapi import APIRouter, Header, Query, HTTPException, Depends
from typing import Optional, List
from datetime import date
import json
import base64

from app.models.api_model import APIResponse
from app.models.oauth_model import OAuthCredentials
from app.models.ga4_model import GA4QueryParams
from app.services.oauth_service import OAuthService
from app.services.ga4_service import GA4Service


router = APIRouter()


def parse_oauth_credentials(x_oauth_credentials: str = Header(...)) -> OAuthCredentials:
    """Parse OAuth credentials from header (base64 encoded JSON)"""
    try:
        decoded = base64.b64decode(x_oauth_credentials).decode('utf-8')
        oauth_data = json.loads(decoded)
        return OAuthCredentials(**oauth_data)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid OAuth credentials in header: {str(e)}"
        )
        

@router.get("/ga4", response_model=APIResponse)
def get_ga4_report(
    property_id: str = Query(..., description="GA4 Property ID"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    metrics: List[str] = Query(["activeUsers"], description="List of metrics"),
    dimensions: Optional[List[str]] = Query(None, description="List of dimensions"),
    limit: int = Query(1000, ge=1, le=10000, description="Result limit"),
    credentials: OAuthCredentials = Depends(parse_oauth_credentials)
):
    """
    Get GA4 analytics report
    
    **Headers:**
    - X-OAuth-Credentials: Base64 encoded JSON with OAuth credentials
   
    """
    try:
        # Create services
        oauth_service = OAuthService(credentials)
        ga4_service = GA4Service(oauth_service)
        
        # Build query params
        query_params = GA4QueryParams(
            property_id=property_id,
            start_date=start_date,
            end_date=end_date,
            metrics=metrics,
            dimensions=dimensions,
            limit=limit
        )
        
        # Execute query
        data = ga4_service.run_report(query_params)
        
        return APIResponse(
            success=True,
            data=data,
            metadata={
                "property_id": property_id,
                "date_range": {
                    "start": query_params.start_date or "yesterday",
                    "end": query_params.end_date or "yesterday"
                }
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
    
    
@router.get("/mailchimp")
def get_mailchimp_data(
    list_id: str = Query(...),
    fields: List[str] = Query(["members", "stats"]),
    credentials: OAuthCredentials = Depends(parse_oauth_credentials)
):
    """Get Mailchimp data"""
    # TODO
