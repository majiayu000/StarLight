USERNAME = os.getenv("DB_USERNAME", "lele")
PASSWORD = os.getenv("DB_PASSWORD", "20090909")
HOST = os.getenv("DB_HOST", "192.168.68.18")
DATABASE = os.getenv("DB_NAME", "lele")

connection_string = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE}"

engine = create_engine(connection_string)