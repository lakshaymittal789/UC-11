import json
import re

data = """
Single Client Multi-Schedule Test Data 

Designed for AI summary testing with longer Care Notes and separate Family Notes 

Client Name 

Margaret Collins 

DOB 

08/14/1942 

Primary Services 

Personal Care, Companion Care 

 

Schedule 1 

Date: 04/01/2026    Caregiver: David Rivera    Service: Personal Care    Status: Completed 

Care Note 1: Client was awake and oriented upon arrival, sitting in the living room and watching television. Morning care was completed with assistance for bathing, grooming, dressing, and oral hygiene. Client required moderate verbal cueing to begin the routine but then followed instructions appropriately and remained cooperative. Skin was observed to be intact with no redness or open areas noted. Breakfast was prepared and the client ate most of the meal, including a full portion of oatmeal and fruit. Hydration was encouraged throughout the visit, and the client accepted fluids without difficulty. Ambulation was completed with a walker and standby support. No falls, no shortness of breath, and no acute pain concerns were observed during this visit. 

Care Note 2: Medication reminders were provided for the morning schedule, and the client was able to state that the medications had already been taken earlier in the day. The caregiver completed light housekeeping, including dishwashing, wiping counters, and changing the bathroom towels. The client was engaged in conversation about the weather and upcoming appointments and appeared calm and pleasant throughout the interaction. A brief safety review was completed near the end of the visit to confirm that pathways remained clear and that frequently used items were within reach. The overall impression from this visit was stable, routine care with no new concerns. 

Care Note 3: Before departure, the caregiver reviewed the care plan tasks scheduled for the week and confirmed that the client wanted assistance with meal setup and extra reminders for hydration. The client tolerated the visit well, maintained a steady mood, and did not demonstrate signs of agitation or distress. Transfer assistance was not required beyond standard standby support, and the client moved from chair to walker with only minimal assistance. The home environment remained clean and safe, and all documented activities were completed as assigned. 

Family Note: Family was updated that the client completed routine personal care, ate well, and remained stable throughout the visit. No new concerns were reported.	 

Schedule 2 

Date: 04/03/2026    Caregiver: Alicia Bennett    Service: Personal Care    Status: Completed 

Care Note 1: Client presented with mild morning fatigue and reported sleeping lightly overnight. The caregiver assisted with transfers from bed to chair and provided support during bathing and dressing. The client required additional time to complete the routine but remained engaged and followed directions well. Appetite was slightly reduced at breakfast, though the client did finish most of the meal after encouragement. The caregiver documented that the client mentioned stiffness in both knees when standing, especially during the first transfer of the day. No swelling, bruising, or visible injury was noted. Because of the stiffness, the caregiver used slower pacing and reminded the client to take rest breaks between activities. 

Care Note 2: The visit included medication reminders, meal preparation, and light housekeeping. The client accepted a glass of juice and a cup of water after being reminded to drink more fluids. Laundry was started and folded before the end of the visit. The caregiver observed that once the client was seated comfortably, mood improved and conversation became more active. The client discussed family plans and seemed reassured after talking through the schedule for the week. There were no incidents, no missed tasks, and no safety hazards noted in the environment. 

Care Note 3: At the end of the visit, the caregiver confirmed that the client was comfortable, had access to needed items, and could reach the call device if assistance was required. The client was left in a safe position with the walker nearby. The overall documentation reflects a slightly slower start to the morning with mild fatigue and stiffness, followed by a steady return to baseline cooperation after support was provided. 

Family Note: Family noted that the client seemed more tired than usual this morning but appreciated that all care was completed safely and that hydration was encouraged. 

Schedule 3 

Date: 04/05/2026    Caregiver: Sonia Patel    Service: Companion Care    Status: Completed 

Care Note 1: The client was seated at the dining table when the caregiver arrived and appeared cheerful and talkative. Companion care activities focused on conversation, meal preparation, and gentle encouragement to remain active during the morning. The client participated in light walking within the home using a walker and needed only standby assistance. Breakfast was prepared according to routine preferences, and the client ate a good portion of the meal. The caregiver noted improved energy compared with the previous visit and observed that the client initiated several conversations without prompting. No pain complaints were voiced, and the client demonstrated stable balance when transitioning between seated and standing positions. 

Care Note 2: The caregiver completed housekeeping tasks including wiping kitchen surfaces, sorting laundry, and removing trash. Medication reminders were provided at the appropriate time, and the client confirmed understanding of the schedule. The client spent time reviewing family photos and discussing upcoming appointments, which appeared to improve mood and engagement. No behavioral concerns, no wandering, and no signs of confusion were documented. The home environment was tidy, and pathways were free of obstacles. Overall, the visit reflected a positive day with improved participation and strong tolerance of routine activities. 

Care Note 3: Before leaving, the caregiver confirmed that the client had water within reach and that all planned tasks were complete. The client thanked the caregiver and remained seated comfortably. Documentation from this visit indicates a stable condition with better energy, improved appetite, and active social engagement throughout the care period. 

Family Note: Family reported that the client seemed brighter today and appreciated the update that mobility and appetite were both improved during the visit. 

Schedule 4 

Date: 04/07/2026    Caregiver: Michael Turner    Service: Personal Care    Status: Completed 

Care Note 1: Upon arrival the caregiver found the client resting in bed but easily awakened. The client reported mild lower back discomfort rated 3/10 during the morning transfer. Support was provided for bathing, dressing, and safe movement from bed to chair. The caregiver used slow pacing and encouraged the client to change positions carefully. After repositioning, the client stated that the discomfort decreased and did not interfere with the remainder of the visit. Skin assessment remained normal, and there were no visible signs of injury, redness, or swelling. The client tolerated grooming and oral care well and was able to complete much of the routine with verbal cueing. 

Care Note 2: Breakfast was prepared and served after personal care was completed. The client ate approximately three quarters of the meal and drank most of a cup of tea. Medication reminders were provided, and the caregiver documented that the client appeared alert, oriented, and receptive to instructions. Household tasks included laundry folding, wiping bathroom surfaces, and organizing supplies for the week. The caregiver also checked that the walker and commonly used items were placed within easy reach. No falls, no respiratory distress, and no safety incidents were observed during the visit. 

Care Note 3: The visit ended with a brief review of the client's comfort level. By departure the client was seated upright and described the back discomfort as manageable. The caregiver advised continued pacing and rest as needed, and the client agreed. Overall, this note reflects a temporary discomfort issue that resolved during the visit and did not prevent completion of routine care tasks. 

Family Note: Family was informed about the mild back discomfort and was reassured that it improved after rest and repositioning with no injury noted. 

Schedule 5 

Date: 04/09/2026    Caregiver: Keisha Williams    Service: Personal Care    Status: Completed 

Care Note 1: The client greeted the caregiver pleasantly and appeared more energetic than on the prior visit. Morning hygiene, dressing, and grooming were completed with only minimal prompting. The client stood with the walker and took several short steps in the hallway with standby support. Balance was steady, and the client expressed satisfaction with the ability to move more freely. Breakfast was prepared with attention to the client's usual preferences, and intake was good. The caregiver noted that the client requested an additional glass of water, which was encouraged and provided. There were no pain complaints, and the client did not show signs of dizziness, shortness of breath, or emotional distress. 

Care Note 2: During the visit the caregiver completed medication reminders, bed linen change, and light housekeeping. The client participated in conversation about family plans and upcoming medical follow-up, showing appropriate attention and recall. A brief review of the day's schedule was completed so the client could anticipate the next visit. The environment remained organized, and no hazards were identified. The client was able to sit and stand multiple times with support only as needed and did not require any emergency intervention. Documentation indicates a stable and positive visit with good cooperation and improved overall stamina. 

Care Note 3: Before leaving, the caregiver confirmed that the client had everything needed for the remainder of the day, including water, the walker, and access to the call button. The client remained in good spirits and thanked the caregiver for the help. This visit suggests steady improvement in mobility and continued stability in mood and routine functioning. 

Family Note: Family was pleased to hear that the client was more active today, had good intake, and completed the routine without any concerns. 

Schedule 6 

Date: 04/11/2026    Caregiver: Nina Brooks    Service: Companion Care    Status: Completed 

Care Note 1: Companion care focused on keeping the client engaged and comfortable during a quiet morning at home. The client was seated in a recliner and responded well to friendly conversation. The caregiver and client reviewed a photo album and discussed several upcoming family events. The client appeared attentive and smiled frequently throughout the interaction. Meal preparation was completed, and the client ate a moderate portion of lunch after initially stating that appetite was not strong. The caregiver encouraged fluids and documented that the client accepted water twice during the visit. No acute medical concerns were observed, though the client reported feeling a little tired after lunch. 

Care Note 2: The caregiver completed housekeeping tasks including kitchen cleanup, bathroom sanitation, and folding a small load of laundry. Medication reminders were provided, and the client confirmed understanding of the schedule for the remainder of the day. The caregiver also made sure that the living space was clear of clutter, especially around the chair and bathroom entrance. The client remained calm, cooperative, and oriented. No confusion, no unsafe behaviors, and no falls occurred during the visit. The client did not request additional assistance beyond routine support, and all tasks were completed successfully. 

Care Note 3: At the end of the visit, the caregiver noted that the client rested comfortably and appeared settled after lunch. The overall tone of the note is one of routine companionship with mild fatigue but no worsening condition. 

Family Note: Family said the client had a quiet day but was comfortable and appreciated the ongoing companionship and reminders provided during the visit. 

Schedule 7 

Date: 04/13/2026    Caregiver: David Rivera    Service: Personal Care    Status: Completed 

Care Note 1: The client was awake but slightly slower to respond than usual when the caregiver arrived. After a brief check-in, the client reported poor sleep and a reduced appetite since the previous day. Morning care was completed with support for bathing, dressing, and toileting. The caregiver documented that the client needed more time to complete transfers and was careful to use the walker with each step. No loss of balance occurred, but the client did appear more cautious than earlier in the month. Breakfast was offered and approximately half was consumed, though the client accepted fluids well. The caregiver watched for signs of dizziness and found none during the visit. 

Care Note 2: The caregiver provided medication reminders, assisted with a short seated rest period, and completed laundry and countertop cleaning. The client mentioned that the knees felt stiff again in the morning, especially after standing from bed. After stretching and a few minutes of rest, movement became easier and the client resumed routine activity. The client remained pleasant and expressed appreciation for the slower pace. There were no incidents, no edema, and no signs of acute injury. The environment was safe and organized, and all essential tasks were completed before the caregiver left. 

Care Note 3: Prior to departure, the caregiver reviewed hydration and encouraged the client to continue resting if needed. The client remained in a stable condition by the end of the visit, but this note captures another brief period of reduced energy and appetite that will likely need continued monitoring. 

Family Note: Family was told the client was tired this morning and ate less than usual, but the care visit was completed safely and the client improved after rest. 

Schedule 8 

Date: 04/15/2026    Caregiver: Alicia Bennett    Service: Personal Care    Status: Completed 

Care Note 1: The client was in better spirits at the start of the visit and greeted the caregiver warmly. Morning bathing, dressing, grooming, and oral hygiene were completed with only light assistance. The client stood more steadily than during the previous visit and walked a short distance to the bathroom with the walker. Appetite was better at breakfast, and the client finished most of the meal. The caregiver observed that the client spoke more clearly and displayed improved stamina throughout the morning. No pain was reported, and the client did not appear short of breath or dizzy at any point. 

Care Note 2: Medication reminders were provided, and the caregiver completed bed linen changes, kitchen cleanup, and trash removal. The client participated in brief conversation about family support and upcoming follow-up care. The caregiver reinforced hydration and asked the client to keep water nearby. The home environment remained tidy and safe, with no obstacles in walkways. The client required only minimal cueing to complete tasks and was able to transition between activities without any issue. This visit reflected a clear improvement from the earlier fatigue and stiffness documented in the month. 

Care Note 3: At the end of the visit, the caregiver confirmed that the client was comfortable, alert, and ready for the rest of the day. The overall observation is a positive one, showing a return toward baseline energy and cooperative participation in care tasks. 

Family Note: Family was pleased to hear that the client was eating better again and showed improved stamina and confidence during mobility tasks. 

Schedule 9 

Date: 04/17/2026    Caregiver: Sonia Patel    Service: Companion Care    Status: Completed 

Care Note 1: The client spent much of the visit in the main living area and was engaged in conversation from the start. Companion care activities included discussion of the day's weather, a review of family photos, and support with a short walk inside the home. The client used the walker appropriately and did not require physical lifting. Meal preparation was completed and the client ate well, including fruit, toast, and soup. The caregiver noted a good mood and no signs of confusion or emotional distress. The client was attentive and asked several relevant questions about the schedule for the next visit. 

Care Note 2: Housekeeping tasks were completed, including dishwashing, wiping the dining table, and straightening the bedroom. Medication reminders were provided at the correct time and the client acknowledged them without difficulty. The caregiver also reviewed the importance of rest after activity and encouraged continued hydration. No dizziness, pain, or falls were documented. The visit remained calm and routine, with strong client participation and good tolerance of social interaction. The environment stayed clean, and all planned tasks were finished on time. 

Care Note 3: Before leaving, the caregiver confirmed the client was comfortable and had a clear view of the call button and water cup. Documentation reflects a stable visit with positive mood, good intake, and no new concerns requiring follow-up. 

Family Note: Family said the client sounded upbeat when they spoke later in the day and appreciated the update that the visit went well. 

Schedule 10 

Date: 04/19/2026    Caregiver: Michael Turner    Service: Personal Care    Status: Completed 

Care Note 1: Client was observed sitting upright and appeared rested on arrival. Morning care was completed with bathing assistance, dressing support, grooming, and oral hygiene. The client moved slowly at first but warmed up as the visit progressed. There were no signs of skin breakdown, pressure areas, or acute pain. The caregiver noted that the client was more talkative than usual and discussed a family birthday coming up later in the week. Breakfast was consumed in full, and the client accepted fluids well. Ambulation within the home was steady and supported only by standby observation. Overall, the client looked well and functioned at a stable baseline during this part of the visit. 

Care Note 2: Medication reminders were provided, and the caregiver completed laundry folding, bathroom wipe-down, and kitchen straightening. The client spent a few minutes organizing personal items and appeared satisfied with the order of the room. The caregiver checked that mobility aids were close by and that the hallway remained clear. No safety concerns, no missed tasks, and no behavioral issues were documented. The client remained cooperative and calm throughout the encounter. Documentation suggests consistent improvement in engagement and appetite compared with the earlier low-energy visits. 

Care Note 3: At the end of the visit, the caregiver reviewed the plan for the next visit and encouraged the client to continue drinking water regularly. The client remained comfortable and thanked the caregiver. The visit ended without incident and with a clear return to routine stability. 

Family Note: Family was informed that the client ate well, moved steadily, and seemed more energetic than during the earlier visits in the month. 

Schedule 11 

Date: 04/21/2026    Caregiver: Keisha Williams    Service: Personal Care    Status: Completed 

Care Note 1: The final visit in this series began with the client alert and in good spirits. Morning hygiene, dressing, and grooming were completed successfully with very little assistance required. The client walked short distances with the walker and showed stable balance when turning and sitting. Appetite remained good and the client finished most of breakfast. The caregiver noted no complaints of knee pain, back discomfort, or dizziness. The client was able to answer questions clearly and remained oriented throughout the visit. Because the client was cooperative and engaged, the care tasks were completed efficiently and without stress. 

Care Note 2: Housekeeping tasks were completed, including surface cleaning, laundry folding, and trash removal. Medication reminders were given, and the caregiver reviewed hydration and rest as part of the usual routine. The client discussed family plans, upcoming appointments, and the weather, demonstrating good attention and memory for the day's events. No incidents or concerns arose during the visit. The environment stayed safe, pathways were clear, and all equipment was in the expected place. The note reflects a stable and comfortable day with no signs of decline. 

Care Note 3: Before departure, the caregiver confirmed that the client had access to water, the walker, and the call device. The client expressed appreciation for the care and appeared calm when the visit ended. Overall, the pattern across the month shows temporary fatigue and stiffness earlier in the period followed by improved appetite, better mobility, and steady cooperation in later visits. 

Family Note: Family appreciated the update that the client ended the month in stable condition and showed better energy, appetite, and mobility than earlier in the period. 

 

Office Notes (Independent of Schedules) 

04/02/2026 — Agency staff confirmed the client care plan review is scheduled for next week and requested that documentation remain focused on routine observations, mobility trends, appetite, and family communication. 

04/06/2026 — Supervisor reviewed recent care notes and asked that any future notes continue capturing changes in sleep, energy, and transfer assistance so trends can be measured over time. 

04/11/2026 — Scheduling team updated the recurring visit pattern and confirmed that no changes were needed to the current caregiver assignment for the client. 

04/17/2026 — Internal review completed with no issues identified. Staff requested that notes remain detailed when describing pain, intake, and any family concerns. 
"""

import re

notes = []
note_id_counter = 1
family_note_id_counter = 1
office_note_id_counter = 1

# Process Schedules
schedules = re.split(r'Schedule \d+', data)
for sched in schedules[1:]:
    # Date: 04/01/2026    Caregiver: David Rivera    Service: Personal Care    Status: Completed
    date_match = re.search(r'Date:\s*(\d{2}/\d{2}/\d{4})', sched)
    caregiver_match = re.search(r'Caregiver:\s*([^\s]+ [^\s]+)', sched)
    if date_match and caregiver_match:
        date_str = date_match.group(1)
        caregiver = caregiver_match.group(1)
        
        iso_date = f"{date_str[6:10]}-{date_str[0:2]}-{date_str[3:5]}T12:00:00Z"
        
        # Care Notes
        care_note_1 = re.search(r'Care Note 1:\s*(.*?)(?=Care Note 2:)', sched, re.DOTALL)
        care_note_2 = re.search(r'Care Note 2:\s*(.*?)(?=Care Note 3:)', sched, re.DOTALL)
        care_note_3 = re.search(r'Care Note 3:\s*(.*?)(?=Family Note:)', sched, re.DOTALL)
        
        if care_note_1 and care_note_2 and care_note_3:
            content = f"Care Note 1: {care_note_1.group(1).strip()}\\n\\nCare Note 2: {care_note_2.group(1).strip()}\\n\\nCare Note 3: {care_note_3.group(1).strip()}"
            notes.append({
                "id": f"note-care-{note_id_counter:03d}",
                "owner_type": "client",
                "owner_id": "client-101",
                "note_type": "care",
                "published": True,
                "content": content,
                "created_by": caregiver,
                "created_at": iso_date,
                "status": "published",
                "includes_office_notes": False,
                "published_at": iso_date,
            })
            note_id_counter += 1
            
        family_note = re.search(r'Family Note:\s*(.*?)(?=\n\s*\n|\Z)', sched, re.DOTALL)
        if family_note:
            notes.append({
                "id": f"note-family-{family_note_id_counter:03d}",
                "owner_type": "client",
                "owner_id": "client-101",
                "note_type": "family",
                "published": True,
                "content": family_note.group(1).strip(),
                "created_by": caregiver,
                "created_at": iso_date,
                "status": "published",
                "includes_office_notes": False,
                "published_at": iso_date,
            })
            family_note_id_counter += 1

# Process Office Notes
office_section = re.search(r'Office Notes \(Independent of Schedules\)(.*?)\Z', data, re.DOTALL)
if office_section:
    office_lines = office_section.group(1).strip().split('\n')
    for line in office_lines:
        line = line.strip()
        if line:
            date_match = re.match(r'(\d{2}/\d{2}/\d{4})\s*—\s*(.*)', line)
            if date_match:
                date_str = date_match.group(1)
                content = date_match.group(2)
                iso_date = f"{date_str[6:10]}-{date_str[0:2]}-{date_str[3:5]}T14:00:00Z"
                notes.append({
                    "id": f"note-office-{office_note_id_counter:03d}",
                    "owner_type": "client",
                    "owner_id": "client-101",
                    "note_type": "office",
                    "published": False,
                    "content": content,
                    "created_by": "scheduler-1",
                    "created_at": iso_date,
                    "status": "internal",
                    "includes_office_notes": True,
                    "published_at": None,
                })
                office_note_id_counter += 1

# Print the resulting python code
out = 'from typing import Any\n\nNoteRecord = dict[str, Any]\n\n\nNOTES: list[NoteRecord] = [\n'
for n in notes:
    out += '    {\n'
    for k, v in n.items():
        if isinstance(v, str):
            # handle newlines
            v = v.replace('\n', '\\n')
            out += f'        "{k}": "{v}",\n'
        elif v is None:
            out += f'        "{k}": None,\n'
        elif isinstance(v, bool):
            out += f'        "{k}": {str(v)},\n'
        else:
            out += f'        "{k}": {v},\n'
    out += '    },\n'
out += ']\n'

with open('c:/Users/cityf/OneDrive/Desktop/uc-11/profile_summary/notes_dummy_data.py', 'w', encoding='utf-8') as f:
    f.write(out)

print("Done writing to notes_dummy_data.py")
