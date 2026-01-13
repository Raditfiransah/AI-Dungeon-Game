from functools import lru_cache
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict 

class Settings(BaseSettings):
    """
    Konfigurasi aplikasi terpusat.
    Menggunakan Pydantic V2 untuk validasi yang lebih ketat.
    """
    
    # Konfigurasi Model 
    model_config = SettingsConfigDict(
        env_file=[".env", "../../.env"], # Prioritas: Local .env (backend), fallback ke root .env
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore" # Penting: Agar tidak error jika ada variable lain di .env
    )

    # SECURITY: Gunakan SecretStr agar API Key tidak bocor di logs/print
    OPENAI_API_KEY: SecretStr = Field(..., description="API Key OpenRouter/OpenAI")

    OPENAI_MODEL: str = Field(default="gpt-4o-mini", description="Model ID yang digunakan")
    OPENAI_BASE_URL: str = Field(default="https://openrouter.ai/api/v1", description="Endpoint URL")

    # VALIDASI: Menambahkan batasan logis (Constraints)
    MAX_TOKENS: int = Field(default=500, gt=0, description="Harus lebih besar dari 0")
    TEMPERATURE: float = Field(default=0.0, ge=0.0, le=2.0, description="Range 0.0 sampai 2.0")

@lru_cache
def get_settings() -> Settings:
    """Singleton pattern untuk settings agar file .env hanya dibaca sekali."""
    return Settings()

# --- Contoh Cara Menggunakan ---
if __name__ == "__main__":
    settings = get_settings()
    
    # Perhatikan cara akses SecretStr
    print(f"Model: {settings.OPENAI_MODEL}")
    print(f"API Key (Masked): {settings.OPENAI_API_KEY}") # Output: **********
    print(f"API Key (Real): {settings.OPENAI_API_KEY.get_secret_value()}") # Output: sk-xxxx...