#!/usr/bin/env python3
"""
Lab 3-2 Part 4: Trigger Retraining Pipeline
Prometheus 메트릭을 모니터링하고 성능 저하 시 자동으로 재학습을 트리거합니다.
"""

import time
import argparse
import requests
from datetime import datetime
import subprocess


class PerformanceMonitor:
    def __init__(self, prometheus_url, mae_threshold, check_interval):
        """
        Args:
            prometheus_url: Prometheus 서버 URL
            mae_threshold: MAE 임계값
            check_interval: 체크 주기 (초)
        """
        self.prometheus_url = prometheus_url
        self.mae_threshold = mae_threshold
        self.check_interval = check_interval
        self.alert_triggered = False
    
    def query_prometheus(self, query):
        """Prometheus PromQL 쿼리 실행"""
        try:
            response = requests.get(
                f"{self.prometheus_url}/api/v1/query",
                params={'query': query}
            )
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'success' and data['data']['result']:
                return float(data['data']['result'][0]['value'][1])
            return None
        
        except Exception as e:
            print(f"  ❌ Prometheus query failed: {e}")
            return None
    
    def check_model_performance(self):
        """모델 성능 체크"""
        # Model A (v1.0)의 MAE 조회
        query = 'model_mae_score{model_name="california-housing", version="v1.0"}'
        mae = self.query_prometheus(query)
        
        if mae is None:
            print(f"  ⚠️  Unable to fetch MAE metric")
            return False
        
        print(f"  Current MAE: {mae:.2f}")
        
        # 임계값 체크
        if mae > self.mae_threshold:
            print(f"  Status: ⚠️  DEGRADED (threshold: {self.mae_threshold:.2f})")
            return True
        else:
            print(f"  Status: ✅ OK")
            return False
    
    def trigger_retraining(self):
        """재학습 파이프라인 트리거"""
        print("\n" + "=" * 60)
        print("  Triggering Retraining Pipeline")
        print("=" * 60)
        print("")
        
        # Step 1: 최근 피드백 데이터 수집
        print("Step 1: Fetching recent A/B test data...")
        time.sleep(2)  # 시뮬레이션
        feedback_samples = 5000
        print(f"✅ Collected {feedback_samples} feedback samples")
        print("")
        
        # Step 2: Kubeflow Pipeline 실행
        print("Step 2: Creating Kubeflow Pipeline Run...")
        run_id = f"run-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}"
        
        # 실제로는 Kubeflow API를 호출하여 파이프라인 실행
        # 여기서는 시뮬레이션
        try:
            # 예시 커맨드 (실제 환경에서 사용)
            # pipeline_yaml = "path/to/retraining_pipeline.yaml"
            # cmd = f"kfp run submit -e default -r {run_id} -f {pipeline_yaml}"
            # subprocess.run(cmd, shell=True, check=True)
            
            print(f"✅ Pipeline created: {run_id}")
            print("")
        except Exception as e:
            print(f"❌ Failed to create pipeline: {e}")
            return
        
        # Step 3: 파이프라인 실행 모니터링
        print("Step 3: Monitoring pipeline execution...")
        
        stages = [
            ("Data preprocessing", 30),
            ("Model training", 105),
            ("Model evaluation", 30),
            ("Model deployment", 15)
        ]
        
        total_time = 0
        for stage, duration in stages:
            time.sleep(2)  # 시뮬레이션
            total_time += duration
            mins = total_time // 60
            secs = total_time % 60
            print(f"  [{mins:02d}:{secs:02d}] {stage} completed")
        
        print("")
        print("✅ Pipeline execution completed successfully!")
        print("")
        
        # Step 4: 새 모델 정보
        print("New Model Metrics:")
        new_mae = 0.36  # 개선된 MAE
        improvement = ((self.mae_threshold - new_mae) / self.mae_threshold) * 100
        print(f"  MAE: {new_mae:.2f} (improved by {improvement:.1f}%)")
        print(f"  R²: 0.87")
        print(f"  Version: v2.1")
        print("")
        
        # Step 5: 배포 상태
        print("Deployment Status:")
        print(f"  InferenceService: model-serving-v2-1")
        print(f"  Status: Ready")
        print(f"  Traffic: 0% → 10% (canary)")
        print("")
    
    def run(self):
        """모니터링 시작"""
        print("=" * 60)
        print("  Model Performance Monitor")
        print("=" * 60)
        print("")
        print("Configuration:")
        print(f"  Prometheus: {self.prometheus_url}")
        print(f"  MAE Threshold: {self.mae_threshold:.2f}")
        print(f"  Check Interval: {self.check_interval} seconds")
        print("")
        print("Starting monitoring...")
        print("Press Ctrl+C to stop")
        print("")
        
        try:
            while True:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] Checking model performance...")
                
                # 성능 체크
                degraded = self.check_model_performance()
                
                # 성능 저하 감지 시 재학습 트리거
                if degraded and not self.alert_triggered:
                    self.trigger_retraining()
                    self.alert_triggered = True
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Resuming monitoring...")
                
                print("")
                time.sleep(self.check_interval)
        
        except KeyboardInterrupt:
            print("\n" + "=" * 60)
            print("  Monitoring Stopped")
            print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='Monitor model performance and trigger retraining'
    )
    parser.add_argument(
        '--prometheus-url',
        default='http://localhost:9090',
        help='Prometheus server URL (default: http://localhost:9090)'
    )
    parser.add_argument(
        '--mae-threshold',
        type=float,
        default=0.40,
        help='MAE threshold for triggering retraining (default: 0.40)'
    )
    parser.add_argument(
        '--check-interval',
        type=int,
        default=60,
        help='Check interval in seconds (default: 60)'
    )
    
    args = parser.parse_args()
    
    monitor = PerformanceMonitor(
        prometheus_url=args.prometheus_url,
        mae_threshold=args.mae_threshold,
        check_interval=args.check_interval
    )
    
    monitor.run()


if __name__ == '__main__':
    main()
