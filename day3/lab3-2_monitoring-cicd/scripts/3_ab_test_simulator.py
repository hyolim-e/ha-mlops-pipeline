#!/usr/bin/env python3
"""
Lab 3-2 Part 2: A/B Test Simulator
Model A와 Model B에 대한 트래픽을 생성하고 성능을 비교합니다.
"""

import time
import argparse
import requests
import numpy as np
from datetime import datetime
from collections import defaultdict


class ABTestSimulator:
    def __init__(self, duration, rps, model_a_ratio=0.5):
        """
        Args:
            duration: 테스트 지속 시간 (초)
            rps: 초당 요청 수
            model_a_ratio: Model A로 보낼 트래픽 비율 (0.0 ~ 1.0)
        """
        self.duration = duration
        self.rps = rps
        self.model_a_ratio = model_a_ratio
        self.model_b_ratio = 1.0 - model_a_ratio
        
        # 통계 수집
        self.stats = {
            'model_a': defaultdict(list),
            'model_b': defaultdict(list)
        }
    
    def generate_sample_data(self):
        """California Housing 데이터 샘플 생성"""
        return {
            'MedInc': np.random.uniform(0.5, 15.0),
            'HouseAge': np.random.uniform(1.0, 52.0),
            'AveRooms': np.random.uniform(1.0, 10.0),
            'AveBedrms': np.random.uniform(0.5, 5.0),
            'Population': np.random.uniform(3.0, 35682.0),
            'AveOccup': np.random.uniform(0.5, 20.0),
            'Latitude': np.random.uniform(32.0, 42.0),
            'Longitude': np.random.uniform(-124.0, -114.0)
        }
    
    def predict_model_a(self, data):
        """
        Model A (v1.0) 예측 시뮬레이션
        점차 성능 저하되는 모델
        """
        # 시간에 따른 성능 저하 시뮬레이션
        elapsed = time.time() - self.start_time
        drift_factor = min(elapsed / self.duration, 1.0)
        
        # MAE: 0.38 → 0.46
        base_mae = 0.38
        mae = base_mae + (0.08 * drift_factor) + np.random.normal(0, 0.02)
        
        # 응답 시간: 40ms ~ 55ms
        latency = 0.040 + np.random.exponential(0.008)
        
        # 성공률: 99%
        success = np.random.random() > 0.01
        
        return {
            'mae': max(0.3, mae),
            'latency': latency,
            'success': success,
            'prediction': np.random.uniform(0.5, 5.0)
        }
    
    def predict_model_b(self, data):
        """
        Model B (v2.0) 예측 시뮬레이션
        안정적이고 개선된 모델
        """
        # MAE: 0.34 ~ 0.39 (안정적)
        mae = 0.36 + np.random.normal(0, 0.015)
        
        # 응답 시간: 45ms ~ 60ms (약간 더 복잡한 모델)
        latency = 0.048 + np.random.exponential(0.010)
        
        # 성공률: 99.5%
        success = np.random.random() > 0.005
        
        return {
            'mae': max(0.3, mae),
            'latency': latency,
            'success': success,
            'prediction': np.random.uniform(0.5, 5.0)
        }
    
    def send_request(self, model):
        """단일 예측 요청 전송"""
        data = self.generate_sample_data()
        
        if model == 'a':
            result = self.predict_model_a(data)
            self.stats['model_a']['mae'].append(result['mae'])
            self.stats['model_a']['latency'].append(result['latency'] * 1000)  # ms
            self.stats['model_a']['success'].append(1 if result['success'] else 0)
        else:
            result = self.predict_model_b(data)
            self.stats['model_b']['mae'].append(result['mae'])
            self.stats['model_b']['latency'].append(result['latency'] * 1000)  # ms
            self.stats['model_b']['success'].append(1 if result['success'] else 0)
    
    def print_stats(self, interval_seconds):
        """현재까지의 통계 출력"""
        model_a_count = len(self.stats['model_a']['mae'])
        model_b_count = len(self.stats['model_b']['mae'])
        total_count = model_a_count + model_b_count
        
        # Model A 통계
        model_a_mae = np.mean(self.stats['model_a']['mae']) if model_a_count > 0 else 0
        model_a_latency = np.mean(self.stats['model_a']['latency']) if model_a_count > 0 else 0
        model_a_success = np.mean(self.stats['model_a']['success']) * 100 if model_a_count > 0 else 0
        
        # Model B 통계
        model_b_mae = np.mean(self.stats['model_b']['mae']) if model_b_count > 0 else 0
        model_b_latency = np.mean(self.stats['model_b']['latency']) if model_b_count > 0 else 0
        model_b_success = np.mean(self.stats['model_b']['success']) * 100 if model_b_count > 0 else 0
        
        print(f"\n[{interval_seconds:02d}:{interval_seconds%60:02d}] Sent {total_count} requests")
        print(f"  Model A (v1.0): MAE={model_a_mae:.2f}, Latency={model_a_latency:.0f}ms, Success={model_a_success:.1f}%")
        print(f"  Model B (v2.0): MAE={model_b_mae:.2f}, Latency={model_b_latency:.0f}ms, Success={model_b_success:.1f}%")
        
        # 성능 저하 알림
        if model_a_mae > 0.40:
            print(f"\n⚠️  Performance Alert!")
            print(f"  Model A MAE ({model_a_mae:.2f}) exceeded threshold (0.40)")
            print(f"  Triggering retraining pipeline...")
    
    def run(self):
        """A/B 테스트 실행"""
        print("=" * 60)
        print("  A/B Test Simulator")
        print("=" * 60)
        print("")
        print("Configuration:")
        print(f"  Duration: {self.duration} seconds ({self.duration//60} minutes)")
        print(f"  Requests per second: {self.rps}")
        print(f"  Model A (v1.0): {self.model_a_ratio*100:.0f}% traffic")
        print(f"  Model B (v2.0): {self.model_b_ratio*100:.0f}% traffic")
        print("")
        print("Starting simulation...")
        
        self.start_time = time.time()
        request_count = 0
        last_report_time = 0
        
        try:
            while time.time() - self.start_time < self.duration:
                # 트래픽 분배 (50/50)
                if np.random.random() < self.model_a_ratio:
                    self.send_request('a')
                else:
                    self.send_request('b')
                
                request_count += 1
                
                # 30초마다 통계 출력
                current_time = int(time.time() - self.start_time)
                if current_time - last_report_time >= 30:
                    self.print_stats(current_time)
                    last_report_time = current_time
                
                # RPS 조절
                time.sleep(1.0 / self.rps)
        
        except KeyboardInterrupt:
            print("\n\nSimulation interrupted by user")
        
        # 최종 통계
        self.print_final_stats()
    
    def print_final_stats(self):
        """최종 통계 출력"""
        print("\n" + "=" * 60)
        print("  Simulation Complete")
        print("=" * 60)
        print("")
        
        model_a_count = len(self.stats['model_a']['mae'])
        model_b_count = len(self.stats['model_b']['mae'])
        total_count = model_a_count + model_b_count
        
        print("Summary:")
        print(f"  Total Requests: {total_count}")
        
        # Model A 최종 통계
        if model_a_count > 0:
            model_a_mae = np.mean(self.stats['model_a']['mae'])
            model_a_latency = np.mean(self.stats['model_a']['latency'])
            model_a_success = np.mean(self.stats['model_a']['success']) * 100
            print(f"  Model A (v1.0): {model_a_count} requests, Avg MAE={model_a_mae:.2f}")
        
        # Model B 최종 통계
        if model_b_count > 0:
            model_b_mae = np.mean(self.stats['model_b']['mae'])
            model_b_latency = np.mean(self.stats['model_b']['latency'])
            model_b_success = np.mean(self.stats['model_b']['success']) * 100
            print(f"  Model B (v2.0): {model_b_count} requests, Avg MAE={model_b_mae:.2f}")
        
        # 승자 결정
        if model_a_count > 0 and model_b_count > 0:
            improvement = ((model_a_mae - model_b_mae) / model_a_mae) * 100
            if model_b_mae < model_a_mae:
                print(f"  Winner: Model B ({improvement:.2f}% improvement)")
            elif model_a_mae < model_b_mae:
                print(f"  Winner: Model A ({-improvement:.2f}% better)")
            else:
                print(f"  Result: Tie")
        
        print("")


def main():
    parser = argparse.ArgumentParser(description='A/B Test Simulator for ML Models')
    parser.add_argument('--duration', type=int, default=300,
                       help='Test duration in seconds (default: 300)')
    parser.add_argument('--requests-per-second', type=int, default=10,
                       help='Requests per second (default: 10)')
    parser.add_argument('--model-a-ratio', type=float, default=0.5,
                       help='Traffic ratio for Model A (default: 0.5)')
    
    args = parser.parse_args()
    
    simulator = ABTestSimulator(
        duration=args.duration,
        rps=args.requests_per_second,
        model_a_ratio=args.model_a_ratio
    )
    
    simulator.run()


if __name__ == '__main__':
    main()
