class BedrockAPIError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class FirestoreError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class GeocodingError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class TicketNotFoundError(FirestoreError):
    def __init__(self, ticket_id: str):
        super().__init__(f"Ticket not found: {ticket_id}")


class AuthenticationError(Exception):
    def __init__(self, message: str = "Unauthorized"):
        self.message = message
        super().__init__(self.message)


class WorkflowError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
