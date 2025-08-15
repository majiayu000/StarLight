# Some Axios Example

1. Use axios to get HttpStatus.302 and it's body from backend.

    Note: It is not a good idea to return 302 from backend. In RESTful, API is stateless which means server-side should not save client status information! Any request should include enough information. 
    A redirect is a state transition operation that indicates that the client should send the request to another URL. In a RESTful architecture, the server should fully represent the state of the resource and the associated operations to the client, rather than simply returning a redirect status code.
    When it comes to state transition, RESTful API should use suitable HTTP code such like 200、 201、 204、 400、 404 to show the result of the request.