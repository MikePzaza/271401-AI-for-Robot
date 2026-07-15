"""
HW_01: จำลองระบบควบคุมอุณหภูมิห้องด้วยแอร์แบบ Closed Loop
Transfer Function: G(s) = K / (tau*s + 1)
Closed Loop Transfer Function: T(s) = G(s) / (1 + G(s)*H(s)), H(s) = 1

คำถาม:
1. ถ้าเปลี่ยน K เป็น 1 ถึง 10 จะส่งผลต่อระบบอย่างไร?
2. ถ้าเพิ่ม tau เป็น 2 ถึง 3 เท่า อุณหภูมิจะเปลี่ยนแปลงช้าหรือเร็วขึ้น หรือเกิดอะไรขึ้น?
3. ทำไมระบบนี้จึงเรียกว่า Closed Loop?
อย่าลืม pip install control matplotlib numpy
"""

import numpy as np
import matplotlib.pyplot as plt
import control as ctrl

# ---------------------------------------------------------
# ฟังก์ชันสร้างระบบ Closed Loop จากค่า K และ tau ที่กำหนด
# ---------------------------------------------------------
def closed_loop_system(K, tau):
    """
    สร้าง Transfer Function แบบ Closed Loop
    G(s) = K / (tau*s + 1)   -> Plant (แอร์)
    H(s) = 1                 -> Feedback (sensor วัดอุณหภูมิจริง)
    T(s) = G(s) / (1 + G(s)*H(s))
    """
    G = ctrl.tf([K], [tau, 1])   # G(s) = K / (tau*s + 1)
    H = ctrl.tf([1], [1])        # H(s) = 1 (unity feedback)
    T = ctrl.feedback(G, H)      # T(s) = G / (1 + G*H)
    return T


# ---------------------------------------------------------
# ค่าเริ่มต้น (Base case)
# ---------------------------------------------------------
K_base = 5      # กำลังทำความเย็นของแอร์
tau_base = 1     # ความเฉื่อยของระบบ (วินาที/นาที)

t = np.linspace(0, 10, 500)

# ===========================================================
# ส่วนที่ 1: ทดลองเปลี่ยนค่า K = 1 ถึง 10 (tau คงที่)
# ===========================================================
plt.figure(figsize=(8, 5))
K_values = [1, 2, 4, 6, 8, 10]

for K in K_values:
    T = closed_loop_system(K, tau_base)
    time, response = ctrl.step_response(T, t)
    plt.plot(time, response, label=f"K = {K}")

plt.title(f"Step Response - Varying K (tau = {tau_base})")
plt.xlabel("Time (s)")
plt.ylabel("Room Temperature Response")
plt.axhline(1, color="gray", linestyle="--", linewidth=0.8, label="Setpoint (Normalized = 1)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("response_vary_K.png", dpi=150)
plt.show()

# ===========================================================
# ส่วนที่ 2: ทดลองเปลี่ยนค่า tau = 1, 2, 3 เท่า (K คงที่)
# ===========================================================
plt.figure(figsize=(8, 5))
tau_values = [1, 2, 3]

for tau in tau_values:
    T = closed_loop_system(K_base, tau)
    time, response = ctrl.step_response(T, t)
    plt.plot(time, response, label=f"tau = {tau}")

plt.title(f"Step Response - Varying tau (K = {K_base})")
plt.xlabel("Time (s)")
plt.ylabel("Room Temperature Response")
plt.axhline(K_base/(1+K_base), color="gray", linestyle="--", linewidth=0.8, label="Steady State Value")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("response_vary_tau.png", dpi=150)
plt.show()

# ===========================================================
# ส่วนที่ 3: วิเคราะห์และพิมพ์คำตอบ
# ===========================================================
print("=" * 60)
print("คำตอบคำถามท้าย HW_01")
print("=" * 60)

print("""
1) ถ้าเปลี่ยน K เป็น 1 ถึง 10 จะส่งผลต่อระบบอย่างไร?
   - เมื่อ K มากขึ้น ระบบตอบสนองเร็วขึ้นและค่า Steady State
     เข้าใกล้ Setpoint (ค่า 1) มากขึ้น เพราะ Steady State =
     K / (1 + K) ซึ่งจะเข้าใกล้ 1 เมื่อ K มีค่าสูงมาก
   - อย่างไรก็ตาม ถ้า K สูงเกินไปในระบบจริง อาจทำให้เกิด
     Overshoot หรือแอร์ทำงานหนักเกินไป (แม้ในระบบ First-order
     นี้จะไม่มี Overshoot ก็ตาม เพราะไม่มีขั้ว complex)

2) ถ้าเพิ่ม tau เป็น 2 ถึง 3 เท่า อุณหภูมิจะเปลี่ยนแปลงช้าลง
   เพราะ tau คือค่าคงที่เวลา (Time Constant) ของระบบ
   ยิ่ง tau มาก ระบบยิ่งตอบสนองช้า (ห้องใหญ่ขึ้น หรือมี inertia
   สูงขึ้น) ทำให้ใช้เวลานานขึ้นกว่าจะเข้าสู่ Steady State
   Time constant ใหม่ของระบบวงปิดคือ tau' = tau / (1+K)

3) ทำไมระบบนี้จึงเรียกว่า Closed Loop?
   เพราะมีการวัดค่าอุณหภูมิจริงจาก sensor (Feedback, H(s))
   แล้วนำค่านั้นย้อนกลับมาเปรียบเทียบกับ Setpoint (Error
   Detection) เพื่อปรับการทำงานของแอร์อย่างต่อเนื่อง ทำให้ระบบ
   สามารถชดเชยผลกระทบจากสิ่งรบกวน (Disturbance) ได้ ต่างจาก
   Open Loop ที่ไม่มีการนำเอาต์พุตย้อนกลับมาตรวจสอบเลย
""")
