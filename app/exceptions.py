from fastapi import HTTPException, status

class CustomExceptions():

    @staticmethod
    def get_credentials_exception(detail="Could not validate credentials"):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

    @staticmethod
    def get_not_authorized_exception(detail="Not authorized"):
        return HTTPException(status_code=403, detail=detail)

    @staticmethod
    def get_bad_request_exception(detail="Bad request"):
        return HTTPException(status_code=400, detail=detail)
    
    @staticmethod
    def not_found_exception(detail="Not found"):
        return HTTPException(status_code=404, detail=detail)
