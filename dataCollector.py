import yfinance as yf
import mysql.connector
from mysql.connector import Error
from circuit_breaker import CircuitBreaker, CircuitBreakerOpenException
import time

# Connettersi al database MySQL
def connect_db():
    return mysql.connector.connect(
        host="db",  # Nome del servizio Docker per MySQL
        user="grpc_user",
        password="grpc_password",
        database="grpc_db"
    )

# Funzione per ottenere il valore corrente di un ticker da yfinance
def fetch_ticker_value(ticker):
    """
    Fetches the latest stock value for the given ticker using yfinance.

    Parameters:
    - ticker (str): The stock ticker to fetch.

    Returns:
    - dict: Contains 'value' (latest stock price) and 'timestamp' (current time).
    """
    stock = yf.Ticker(ticker)
    history = stock.history(period="1d")
    if history.empty:
        raise Exception(f"No data available for ticker {ticker}")
    latest_close = history['Close'].iloc[-1]
    timestamp = history.index[-1].isoformat()
    return {"value": latest_close, "timestamp": timestamp}

# Circuit Breaker per proteggere le chiamate a yfinance
circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=10)

def collect_data():
    """
    Periodically collects data for all users' tickers and updates the database.
    """
    try:
        # Connessione al database
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)

        while True:
            # Recupera i tickers dalla tabella Utenti
            cursor.execute("SELECT mail, ticker FROM Utenti")
            users = cursor.fetchall()

            for user in users:
                mail = user['mail']
                ticker = user['ticker']
                try:
                    # Usa il Circuit Breaker per chiamare fetch_ticker_value
                    data = circuit_breaker.call(fetch_ticker_value, ticker)
                    print(f"Fetched data for {ticker}: {data}")

                    # Inserisci i dati nella tabella Operazioni
                    cursor.execute(
                        "INSERT INTO Operazioni (mail_utente, valore, timestamp) VALUES (%s, %s, %s)",
                        (mail, data['value'], data['timestamp'])
                    )
                    conn.commit()
                except CircuitBreakerOpenException:
                    print(f"Skipping ticker {ticker}: Circuit breaker is open.")
                except Exception as e:
                    print(f"Error fetching data for {ticker}: {e}")

            # Aspetta 60 secondi prima della prossima iterazione
            time.sleep(60)

    except Error as e:
        print(f"Database error: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    collect_data()
