AppDaemon Modular Automation 구조
=================================

구성 요약
--------
- 코어 레이어: `base/room_core.py`와 `base/mode_core.py`가 방/모드별 YAML 설정을 읽어 Feature 클래스를 동적으로 로드합니다. 모든 공통 토큰(`room_id`, `mode_id`, guard 등)을 주입해 재사용성을 확보했습니다.
- 룸 기능(Features): `base/room_features/` 폴더의 작은 클래스들이 단일 책임(수동모드, 존재감 조명, 라스트라이트 트래커, 샤워/습도 팬, 슬립 라이트, 야외 스위치 등)을 담당합니다. 새로운 방은 YAML에 feature 블록만 추가하면 됩니다.
- 모드 기능(Features): `base/mode_features/` 폴더가 글로벌 모드(낮잠, 영화, 요리, 외출, 릴랙스, 문 알림, 리페어 등)를 캡슐화합니다. 토글/미디어/타이머/알림/깜빡임 등의 패턴을 재사용합니다.
- 헬퍼 관리: `helpers/global_helper_manager.yaml` + `base/helper_manager.py`가 input_boolean/number/select/timer/template 센서를 AppDaemon에서 생성·관리해 확장성과 백업을 제공합니다.

주요 이전 포인트 (HA automations → AppDaemon)
--------------------------------------------
- Room3 전환
  - 수동 모드, 카운터 기반 조명, 라스트 라이트, 낮잠/취침, 노브 제어 모두 AppDaemon 기능으로 구현.
  - 취침 모드: `room3_sleep_mode.yaml`에 transition(3초) 추가, `sleepmode_off` feature가 취침 해제 시 `input_boolean.room3_manualmode_on`도 함께 OFF.
  - 기상(취침 해제) 시 밝기/색온도/트랜지션 및 날씨 알림을 기존 자동화와 동일하게 유지.
- 모드/특수 시나리오
  - 영화, 요리, 외출, 문 경보, 낮잠, 릴랙스, 리페어 모드 모두 ModeFeature로 매핑되어 확장 가능.
  - 깜빡임/스냅샷/알림/타이머 동작을 설정 기반으로 재사용.
- 공간별 조명/환풍
  - 부엌/바/거실: presence_lighting + manual_mode로 물리 스위치/수동 타임아웃/안전 체크 처리.
  - 욕실1/2: people 카운터 + 레이더 기반 조명, 습도-팬, 샤워 감지, 기본 밝기/색온도 싱크.
  - 발코니: 일몰 이후 동작하는 존재감 스위치.

확장 가이드
-----------
- 새 방 추가: `apps/<room>/<room>_room_core.yaml`에 room_id, guard, features만 정의하면 코어가 자동 로드.
- 기능 추가: 공통 로직은 Feature 클래스로 분리 후 `FEATURE_REGISTRY`에 등록, YAML에서 `type:`으로 참조.
- 모드 추가: `apps/special_modes/*.yaml`에 mode_id와 feature 조합을 선언하면 끝. 미디어/타이머/알림 패턴을 재사용.
- 토큰/엔티티 재사용: YAML에서 `{room}` 등 토큰 사용 가능. 엔티티 ID는 기존 HA와 동일하게 유지해 충돌을 방지합니다.

폴더 구조
---------
```
appdaemon_config/
├─ appdaemon.yaml              # AppDaemon 설정
├─ apps/
│  ├─ apps.yaml                # 모든 앱 선언 (helpers, rooms, modes)
│  ├─ base/                    # 코어/feature 파이썬 모듈
│  │  ├─ room_core.py, mode_core.py
│  │  ├─ room_features/        # 방 단위 기능
│  │  └─ mode_features/        # 모드 단위 기능
│  ├─ helpers/                 # HelperManager 정의
│  ├─ room3/                   # Room3 설정 YAML
│  ├─ bathroom/                # 욕실 1/2 설정 YAML
│  ├─ kitchen/                 # 부엌/바 설정 YAML
│  ├─ living/                  # 거실 설정 YAML
│  ├─ outdoor/                 # 발코니 등 외부
│  └─ special_modes/           # 낮잠/영화/요리/외출/문알림/릴랙스/리페어 모드
└─ APPDAEMON_STRUCTURE.md      # 구조 정리 문서
```

강점
--------------
- 선언적 구성: 모든 로직을 YAML에서 선언하고, 파이썬은 작은 Feature 단위로만 책임을 집니다.
- 재사용성: presence, manual mode, humidity, movie, cooking 등 공통 시나리오를 Feature로 캡슐화하여 복붙 없이 확장.
- 가드/세이프티: `guard_entity`로 글로벌 정지(Repair), safety check/force-off/타이머가 내장되어 오동작을 최소화.
- 확장성: 방/모드 추가 시 코드 변경 없이 YAML만 추가
