from pydantic import BaseModel

# 가짜 생성자 클래스를 정의
class Dummy:
    def __init__(self, license_plate, default_type=False):
        print(f"✅ 생성자 호출됨: license_plate={license_plate}, default_type={default_type}")

# Pydantic 모델 정의
class VehicleCreate(BaseModel):
    license_plate: str
    default_type: bool

# 데이터 입력
data = VehicleCreate(license_plate="123가4567", default_type=True)

# exclude로 default_type 제거
filtered_data = data.model_dump(exclude={"default_type"})
print("📦 exclude된 dict:", filtered_data)

# 딕셔너리를 **으로 풀어서 전달 (default_type 없음)
print("🚗 Dummy 생성:")
vehicle = Dummy(filtered_data)  # default_type은 전달되지 않음 → 기본값 False 사용됨

print(vehicle)