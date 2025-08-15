use actix_web::{get, post, web, App, HttpResponse, HttpServer, Responder};

#[get("/")]
async fn hello() -> impl Responder {
    HttpResponse::Ok().body("Rest Api!")
}

#[post("/echo")]
async fn echo(_req_body: String) -> impl Responder {
    HttpResponse::Ok().body("_req_body")
}

async fn manual_hello() -> impl Responder {
    HttpResponse::Ok().body("Hey Actix!")
}


#[actix_web::main]
async fn main() -> std::io::Result<()>  {
    HttpServer::new(||{
        App::new()
            .service(hello)
            .service(echo)
            .route("/hey", web::get().to(manual_hello))
        })
        .bind(("127.0.0.1", 8080))?
        .run()
        .await
}