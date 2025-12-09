# Lab 1-2: Jupyter Notebook에서 파이프라인 작성하기

## 📋 개요

이 가이드는 Jupyter Notebook 환경에서 Kubeflow Pipeline을 작성하고 실행하는 방법을 설명합니다.

**⚠️ 중요:** Jupyter Notebook 사용은 선택사항입니다. 메인 README.md의 터미널 기반 실습만으로도 충분합니다.

---

## 🎯 Jupyter Notebook 장점

- **인터랙티브 개발**: 코드를 셀 단위로 실행하며 결과 즉시 확인
- **문서화**: 마크다운과 코드를 함께 작성
- **시각화**: 파이프라인 구조를 그래프로 표시
- **디버깅**: 단계별 실행으로 오류 쉽게 발견

---

## 🚀 Jupyter Notebook 시작하기

### Step 1: Jupyter Notebook 서버 접속

**Kubeflow Dashboard에서:**

1. 왼쪽 메뉴에서 **"Notebooks"** 클릭
2. 본인의 Notebook Server 찾기 (예: `user01-notebook`)
3. **"CONNECT"** 버튼 클릭

**또는 포트 포워딩:**
```bash
export USER_NUM="01"
kubectl port-forward svc/user${USER_NUM}-notebook -n kubeflow-user${USER_NUM} 8888:80
```

브라우저에서 접속:
```
http://localhost:8888
```

### Step 2: 새 Notebook 생성

1. **"New"** 드롭다운 클릭
2. **"Python 3"** 선택
3. Notebook 이름 변경: `hello_pipeline.ipynb`

---

## 📝 Notebook에서 파이프라인 작성

### Cell 0: 패키지 설치 및 임포트

```python
# KFP SDK 설치 (필요한 경우)
!pip install kfp>=2.0.0

# 패키지 임포트
from kfp import dsl
from kfp import compiler
```

**실행:** `Shift + Enter`

**예상 출력:**
```
Requirement already satisfied: kfp>=2.0.0 in /opt/conda/lib/python3.11/site-packages
```

### Cell 1: Component 정의 - add

```python
@dsl.component(base_image='python:3.11')
def add(a: int, b: int) -> int:
    """
    두 숫자를 더합니다.
    
    Args:
        a: 첫 번째 숫자
        b: 두 번째 숫자
    
    Returns:
        int: 두 숫자의 합
    """
    result = a + b
    print(f"Add: {a} + {b} = {result}")
    return result
```

**실행 후:** "Function successfully defined" (표시 없음, 정상)

### Cell 2: Component 정의 - multiply

```python
@dsl.component(base_image='python:3.11')
def multiply(x: int, factor: int = 2) -> int:
    """
    숫자에 factor를 곱합니다.
    
    Args:
        x: 입력 숫자
        factor: 곱할 값 (기본값: 2)
    
    Returns:
        int: 곱셈 결과
    """
    result = x * factor
    print(f"Multiply: {x} * {factor} = {result}")
    return result
```

### Cell 3: Component 정의 - print_result

```python
@dsl.component(base_image='python:3.11')
def print_result(value: int):
    """
    최종 결과를 출력합니다.
    
    Args:
        value: 출력할 값
    """
    print("=" * 50)
    print(f"Final Result: {value}")
    print("=" * 50)
```

### Cell 4: Pipeline 정의

```python
@dsl.pipeline(
    name='Hello World Pipeline',
    description='Simple addition and multiplication pipeline'
)
def hello_pipeline(
    a: int = 3,
    b: int = 5,
    factor: int = 2
):
    """
    Hello World Pipeline
    
    계산: (a + b) * factor
    
    Args:
        a: 첫 번째 숫자 (기본값: 3)
        b: 두 번째 숫자 (기본값: 5)
        factor: 곱할 값 (기본값: 2)
    """
    
    # Step 1: a + b 계산
    add_task = add(a=a, b=b)
    
    # Step 2: (a + b) * factor 계산
    multiply_task = multiply(
        x=add_task.output,
        factor=factor
    )
    
    # Step 3: 결과 출력
    print_result(value=multiply_task.output)
```

### Cell 5: 파이프라인 컴파일

```python
# YAML 파일로 컴파일
output_file = 'hello_pipeline.yaml'

compiler.Compiler().compile(
    pipeline_func=hello_pipeline,
    package_path=output_file
)

print(f"✅ 파이프라인 컴파일 완료: {output_file}")
```

**예상 출력:**
```
✅ 파이프라인 컴파일 완료: hello_pipeline.yaml
```

### Cell 6: 컴파일된 YAML 확인 (선택사항)

```python
# YAML 파일 내용 확인
with open(output_file, 'r') as f:
    yaml_content = f.read()
    print(yaml_content[:500])  # 처음 500자만 출력
```

---

## 🔄 로컬에서 Component 테스트

Kubeflow에 업로드하기 전에 Component 함수를 로컬에서 테스트할 수 있습니다.

### Cell 7: Component 로컬 테스트

```python
# Component를 일반 함수처럼 호출하여 테스트
print("=== 로컬 테스트 시작 ===\n")

# Step 1: add 테스트
a, b = 10, 20
sum_result = add.python_func(a, b)
print(f"Step 1 결과: {sum_result}\n")

# Step 2: multiply 테스트
factor = 3
product_result = multiply.python_func(sum_result, factor)
print(f"Step 2 결과: {product_result}\n")

# Step 3: print_result 테스트
print_result.python_func(product_result)

print("\n=== 로컬 테스트 완료 ===")
```

**예상 출력:**
```
=== 로컬 테스트 시작 ===

Add: 10 + 20 = 30
Step 1 결과: 30

Multiply: 30 * 3 = 90
Step 2 결과: 90

==================================================
Final Result: 90
==================================================

=== 로컬 테스트 완료 ===
```

---

## 📤 Kubeflow UI로 업로드

### 방법 1: 파일 다운로드 후 업로드

1. Jupyter Notebook에서 `hello_pipeline.yaml` 파일 선택
2. 체크박스 선택 후 **"Download"** 클릭
3. Kubeflow Dashboard → Pipelines → Upload pipeline
4. 다운로드한 파일 선택

### 방법 2: Kubeflow Client 사용 (고급)

```python
# Cell 8: Kubeflow Client로 직접 업로드 (선택사항)
import kfp

# Kubeflow Pipelines 클라이언트 초기화
client = kfp.Client(host='http://ml-pipeline-ui.kubeflow-user01.svc.cluster.local:80')

# 파이프라인 업로드
pipeline = client.upload_pipeline(
    pipeline_package_path=output_file,
    pipeline_name='Hello World Pipeline'
)

print(f"✅ 파이프라인 업로드 완료!")
print(f"Pipeline ID: {pipeline.id}")
```

**⚠️ 주의:** 이 방법은 Notebook Server가 클러스터 내부에 있을 때만 작동합니다.

---

## 🎯 Notebook 장단점

### ✅ 장점

- **인터랙티브**: 셀 단위로 실행하며 즉시 결과 확인
- **디버깅 용이**: 각 단계별로 테스트 가능
- **문서화**: 설명과 코드를 함께 작성
- **시각화**: 결과를 그래프로 표시 가능

### ⚠️ 단점

- **버전 관리 어려움**: `.ipynb` 파일은 Git에 적합하지 않음
- **재현성**: 셀 실행 순서에 따라 결과가 달라질 수 있음
- **배포**: 프로덕션 환경에는 `.py` 파일이 더 적합

### 💡 권장 사항

- **개발 단계**: Jupyter Notebook 사용 (빠른 프로토타이핑)
- **배포 단계**: Python 스크립트 사용 (`.py`)

---

## 📚 추가 리소스

### Notebook에서 파이프라인 시각화

```python
# Cell 9: 파이프라인 구조 출력
import kfp.dsl as dsl

# 파이프라인을 컴파일하면서 구조 확인
compiler.Compiler().compile(
    pipeline_func=hello_pipeline,
    package_path='temp.yaml'
)

print("✅ 파이프라인 구조가 temp.yaml에 저장되었습니다.")
print("Kubeflow UI의 'Graph' 탭에서 시각화를 확인하세요.")
```

---

## ✅ Notebook 체크리스트

- [ ] Jupyter Notebook 서버 접속
- [ ] 새 Notebook 생성 (`hello_pipeline.ipynb`)
- [ ] KFP SDK 임포트
- [ ] Component 3개 정의 (add, multiply, print_result)
- [ ] Pipeline 정의
- [ ] 파이프라인 컴파일
- [ ] 로컬 테스트 성공
- [ ] YAML 파일 다운로드
- [ ] Kubeflow UI에 업로드

---

## 💡 문제 해결

### 문제: "ModuleNotFoundError: No module named 'kfp'"

**해결:**
```python
# Cell에서 직접 설치
!pip install --upgrade kfp>=2.0.0
```

### 문제: Notebook 저장 안 됨

**해결:**
```python
# 수동 저장
import time
print(f"마지막 저장 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")

# Jupyter 메뉴: File → Save and Checkpoint
```

### 문제: Kernel Restart

**해결:**
- Kernel → Restart & Run All
- 모든 셀을 순서대로 다시 실행

---

## 📖 참고 자료

- [Jupyter Notebook 공식 문서](https://jupyter-notebook.readthedocs.io/)
- [KFP SDK v2 Notebook 예제](https://github.com/kubeflow/pipelines/tree/master/samples/core)

---

© 2025 현대오토에버 MLOps Training
