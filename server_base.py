import grpc
from concurrent import futures
import financial_service_pb2 as pb2
import financial_service_pb2_grpc as pb2_grpc

# Implementazione del servizio gRPC
class FinancialService(pb2_grpc.FinancialServiceServicer):
    def RegisterUser(self, request, context):
        # Logica per registrare un utente
        print(f"Registering user: {request.email} with ticker: {request.ticker}")
        # Simula un successo
        return pb2.UserResponse(success=True, message="User registered successfully")

    def UpdateUser(self, request, context):
        # Logica per aggiornare un utente
        print(f"Updating user: {request.email} with new ticker: {request.ticker}")
        # Simula un successo
        return pb2.UserResponse(success=True, message="User updated successfully")

    def DeleteUser(self, request, context):
        # Logica per cancellare un utente
        print(f"Deleting user: {request.email}")
        # Simula un successo
        return pb2.UserResponse(success=True, message="User deleted successfully")

    def GetLatestValue(self, request, context):
        # Logica per recuperare l'ultimo valore disponibile (simulata)
        print(f"Getting latest value for ticker of user: {request.email}")
        # Simula un valore
        return pb2.StockValueResponse(success=True, value=150.75, timestamp="2024-11-12T10:00:00Z")

    def GetAverageValue(self, request, context):
        # Logica per calcolare la media degli ultimi X valori (simulata)
        print(f"Calculating average of last {request.count} values for user: {request.email}")
        # Simula un valore medio
        return pb2.StockValueResponse(success=True, value=145.67, timestamp="2024-11-12T10:00:00Z")

# Funzione principale per avviare il server
def serve():
    # Creazione del server gRPC
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_FinancialServiceServicer_to_server(FinancialService(), server)
    server.add_insecure_port('[::]:50051')  # Porta su cui il server ascolta
    print("Server started on port 50051")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
