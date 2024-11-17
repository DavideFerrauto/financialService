import grpc
from concurrent import futures
import financial_service_pb2 as pb2
import financial_service_pb2_grpc as pb2_grpc
import mysql.connector
from mysql.connector import Error

# Connettersi al database MySQL
def connect_db():
    return mysql.connector.connect(
        host="db",  # Nome del servizio Docker per MySQL
        user="grpc_user",
        password="grpc_password",
        database="grpc_db"
    )

class FinancialService(pb2_grpc.FinancialServiceServicer):
    def __init__(self):
        self.conn = connect_db()
        self.cur = self.conn.cursor()
        self.setup_database()

    def setup_database(self):
        # Creazione delle tabelle
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS Utenti (
            id INT AUTO_INCREMENT PRIMARY KEY,
            mail VARCHAR(100) UNIQUE,
            ticker VARCHAR(10)
        )
        """)
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS Operazioni (
            id INT AUTO_INCREMENT PRIMARY KEY,
            id_utente INT,
            valore FLOAT,
            timestamp DATETIME,
            FOREIGN KEY (id_utente) REFERENCES Utenti(id) ON DELETE CASCADE
        )
        """)
        self.conn.commit()

    def RegisterUser(self, request, context):
        try:
            self.cur.execute(
                "INSERT INTO Utenti (mail, ticker) VALUES (%s, %s)",
                (request.email, request.ticker)
            )
            self.conn.commit()
            return pb2.UserResponse(success=True, message="User registered successfully")
        except Error as e:
            self.conn.rollback()
            return pb2.UserResponse(success=False, message=str(e))

    def UpdateUser(self, request, context):
        self.cur.execute(
            "UPDATE Utenti SET ticker = %s WHERE mail = %s",
            (request.ticker, request.email)
        )
        self.conn.commit()
        return pb2.UserResponse(success=True, message="User updated successfully")

    def DeleteUser(self, request, context):
        self.cur.execute(
            "DELETE FROM Utenti WHERE mail = %s",
            (request.email,)
        )
        self.conn.commit()
        return pb2.UserResponse(success=True, message="User deleted successfully")

    def GetLatestValue(self, request, context):
        self.cur.execute(
            "SELECT valore, timestamp FROM Operazioni WHERE mail_utente = %s ORDER BY timestamp DESC LIMIT 1",
            (request.email,)
        )
        result = self.cur.fetchone()
        if result:
            valore, timestamp = result
            return pb2.StockValueResponse(success=True, value=valore, timestamp=str(timestamp))
        return pb2.StockValueResponse(success=False, message="No data found")

    def GetAverageValue(self, request, context):
        self.cur.execute(
            "SELECT AVG(valore) FROM Operazioni WHERE mail_utente = %s",
            (request.email,)
        )
        result = self.cur.fetchone()
        if result and result[0] is not None:
            return pb2.StockValueResponse(success=True, value=result[0], timestamp="")
        return pb2.StockValueResponse(success=False, message="No data found")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_FinancialServiceServicer_to_server(FinancialService(), server)
    server.add_insecure_port('[::]:50051')
    print("Server running on port 50051")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
