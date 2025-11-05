import pandas as pd
import random
import streamlit as st
from datetime import datetime

class WorkoutGenerator:
    def __init__(self, csv_file='data/exercises.csv'):
        try:
            self.df = pd.read_csv(csv_file)
            # Clean the data
            self.df['Equipment'] = self.df['Equipment'].fillna('None')
            self.df['Body Focus'] = self.df['Body Focus'].fillna('')
            self.df['Goal'] = self.df['Goal'].fillna('')
        except FileNotFoundError:
            st.error(f"Exercise database not found at {csv_file}")
            self.df = pd.DataFrame(columns=['Exercise Name', 'Category', 'Intensity', 'Equipment', 'Body Focus', 'Goal', 'Workload Match'])
        
        # Enhanced mapping with all possible combinations
        self.body_focus_map = {
            '🔄 Full Body': ['Full body', 'Full Body'],
            '💪 Upper Body': ['Arms', 'Shoulders', 'Chest', 'Back', 'Upper body', 'Upper Body'],
            '🦵 Lower Body': ['Legs', 'Glutes', 'Lower body', 'Lower Body', 'Thighs', 'Calves', 'Hamstrings'],
            '🎯 Core': ['Core', 'Abs', 'Obliques', 'Abdominals'],
            '🧘 Flexibility': ['Spine', 'Hamstrings', 'Hips', 'Flexibility', 'Back', 'Shoulders']
        }
        
        self.emotion_intensity_map = {
            '😴 Tired': 'Low',
            '😌 Calm': 'Low',
            '🎯 Focused': 'Moderate', 
            '💪 Energetic': 'High'
        }
        
        self.need_goal_map = {
            '⚡ Quick Energy': ['Energy Boost', 'Fat loss', 'Endurance'],
            '😌 Stress Relief': ['Stress Relief', 'Relaxation', 'Calmness', 'Mindfulness'],
            '💪 Full Workout': ['Strength', 'Fat loss', 'Endurance', 'Core Strength'],
            '🪑 Desk Relief': ['Flexibility', 'Mobility', 'Posture', 'Balance']
        }
        
        self.equipment_map = {
            '👤 Nothing': ['None'],
            '🧘 Yoga Mat': ['None', 'Mat'],
            '🏋️ Dumbbells': ['None', 'Dumbbell', 'Dumbbells'],
            '💪 Bands': ['None', 'Resistance Band']
        }
        
        self.time_structure = {
            '15min ⚡': {'rounds': 2, 'exercises': 4, 'total_time': 15},
            '30min 🕒': {'rounds': 3, 'exercises': 6, 'total_time': 30},
            '45min ⏱️': {'rounds': 3, 'exercises': 6, 'total_time': 45},
            '60min 🕛': {'rounds': 4, 'exercises': 8, 'total_time': 60}
        }

    def get_exercise_sets_reps(self, exercise_name, category):
        """Determine sets/reps based on exercise type"""
        sets_reps_map = {
            'Strength': "3 sets of 8-12 reps",
            'Cardio': "30-60 seconds intervals",
            'Yoga': "30-90 seconds hold",
            'Breathing': "5-10 deep breaths",
            'Meditation': "2-5 minutes",
            'Flexibility': "30-60 seconds per side"
        }
        return sets_reps_map.get(category, "12-15 reps")

    def _filter_exercises_by_equipment(self, exercises, equipment_preference):
        """Filter exercises by equipment preference with priority"""
        target_equipment = self.equipment_map.get(equipment_preference, ['None'])
        
        # First try exact equipment match
        exact_match = exercises[exercises['Equipment'].isin(target_equipment)]
        
        if len(exact_match) >= 4:
            return exact_match
        
        # If not enough, include exercises that require less equipment
        all_equipment = ['None', 'Mat', 'Dumbbell', 'Resistance Band', 'Chair', 'Wall']
        equipment_priority = {
            '👤 Nothing': ['None'],
            '🧘 Yoga Mat': ['None', 'Mat'],
            '🏋️ Dumbbells': ['None', 'Mat', 'Dumbbell'],
            '💪 Bands': ['None', 'Mat', 'Resistance Band']
        }
        
        fallback_equipment = equipment_priority.get(equipment_preference, ['None'])
        fallback_match = exercises[exercises['Equipment'].isin(fallback_equipment)]
        
        return fallback_match if len(fallback_match) >= 4 else exercises

    def _filter_exercises_by_body_focus(self, exercises, body_focus):
        """Filter exercises by body focus with intelligent matching"""
        target_focus_areas = self.body_focus_map.get(body_focus, [])
        
        if not target_focus_areas:
            return exercises
        
        # Find exercises that match any of the target focus areas
        def matches_focus(body_focus_str):
            if pd.isna(body_focus_str):
                return False
            return any(focus_area.lower() in body_focus_str.lower() for focus_area in target_focus_areas)
        
        focused_exercises = exercises[exercises['Body Focus'].apply(matches_focus)]
        
        if len(focused_exercises) >= 4:
            return focused_exercises
        
        # If not enough, return original exercises but prioritize matching ones
        return exercises

    def _filter_exercises_by_goal(self, exercises, need):
        """Filter exercises by user's goal/need"""
        target_goals = self.need_goal_map.get(need, [])
        
        if not target_goals:
            return exercises
        
        def matches_goal(goal_str):
            if pd.isna(goal_str):
                return False
            return any(goal.lower() in goal_str.lower() for goal in target_goals)
        
        goal_matched = exercises[exercises['Goal'].apply(matches_goal)]
        
        if len(goal_matched) >= 4:
            return goal_matched
        
        return exercises

    def _filter_exercises_by_intensity(self, exercises, emotion):
        """Filter exercises by intensity based on emotion"""
        target_intensity = self.emotion_intensity_map.get(emotion, 'Moderate')
        
        intensity_matched = exercises[exercises['Intensity'] == target_intensity]
        
        if len(intensity_matched) >= 4:
            return intensity_matched
        
        # Allow some flexibility in intensity
        intensity_order = ['Low', 'Moderate', 'High']
        try:
            target_idx = intensity_order.index(target_intensity)
            # Include one level above and below
            allowed_intensities = []
            if target_idx > 0:
                allowed_intensities.append(intensity_order[target_idx - 1])
            allowed_intensities.append(target_intensity)
            if target_idx < len(intensity_order) - 1:
                allowed_intensities.append(intensity_order[target_idx + 1])
            
            flexible_match = exercises[exercises['Intensity'].isin(allowed_intensities)]
            return flexible_match
        except ValueError:
            return exercises

    def _select_varied_exercises(self, exercises_df, num_exercises):
        """Select exercises ensuring variety in categories"""
        if len(exercises_df) <= num_exercises:
            return exercises_df.sample(frac=1)  # Shuffle all exercises
        
        # Group by category and select evenly
        categories = exercises_df['Category'].unique()
        selected_exercises = pd.DataFrame()
        
        exercises_per_category = max(1, num_exercises // len(categories))
        
        for category in categories:
            category_exercises = exercises_df[exercises_df['Category'] == category]
            if len(category_exercises) > 0:
                sample_size = min(exercises_per_category, len(category_exercises))
                selected_exercises = pd.concat([
                    selected_exercises, 
                    category_exercises.sample(n=sample_size)
                ])
        
        # If we need more exercises, fill randomly
        if len(selected_exercises) < num_exercises:
            remaining = num_exercises - len(selected_exercises)
            remaining_exercises = exercises_df[~exercises_df.index.isin(selected_exercises.index)]
            if len(remaining_exercises) > 0:
                selected_exercises = pd.concat([
                    selected_exercises,
                    remaining_exercises.sample(n=min(remaining, len(remaining_exercises)))
                ])
        
        return selected_exercises.sample(frac=1)  # Final shuffle

    def generate_workout(self, emotion, time_available, equipment, need, body_focus):
        try:
            # Start with all exercises
            filtered_exercises = self.df.copy()
            
            # Apply filters in order of importance
            st.write("🔍 Filtering exercises...")
            
            # 1. Filter by equipment (most important - user has limited equipment)
            filtered_exercises = self._filter_exercises_by_equipment(filtered_exercises, equipment)
            st.write(f"   ✅ After equipment filter: {len(filtered_exercises)} exercises")
            
            # 2. Filter by body focus
            filtered_exercises = self._filter_exercises_by_body_focus(filtered_exercises, body_focus)
            st.write(f"   ✅ After body focus filter: {len(filtered_exercises)} exercises")
            
            # 3. Filter by goal/need
            filtered_exercises = self._filter_exercises_by_goal(filtered_exercises, need)
            st.write(f"   ✅ After goal filter: {len(filtered_exercises)} exercises")
            
            # 4. Filter by intensity
            filtered_exercises = self._filter_exercises_by_intensity(filtered_exercises, emotion)
            st.write(f"   ✅ After intensity filter: {len(filtered_exercises)} exercises")
            
            # If we have very few exercises, show what we're working with
            if len(filtered_exercises) < 4:
                st.warning(f"Only found {len(filtered_exercises)} matching exercises. Expanding search criteria...")
                # Start over with just equipment requirement
                filtered_exercises = self._filter_exercises_by_equipment(self.df.copy(), equipment)
            
            # Select exercises based on time structure
            time_data = self.time_structure[time_available]
            num_exercises = min(time_data['exercises'], len(filtered_exercises))
            
            if num_exercises == 0:
                st.error("❌ No exercises found with current criteria. Please adjust your selections.")
                return None
            
            # Ensure variety in selection
            selected_exercises = self._select_varied_exercises(filtered_exercises, num_exercises)
            
            # Generate workout plan
            workout_plan = {
                'rounds': time_data['rounds'],
                'total_time': time_data['total_time'],
                'filters_applied': {
                    'equipment': equipment,
                    'body_focus': body_focus,
                    'goal': need,
                    'intensity': emotion
                },
                'exercises': []
            }
            
            for _, exercise in selected_exercises.iterrows():
                workout_plan['exercises'].append({
                    'name': exercise['Exercise Name'],
                    'sets_reps': self.get_exercise_sets_reps(exercise['Exercise Name'], exercise['Category']),
                    'category': exercise['Category'],
                    'intensity': exercise['Intensity'],
                    'equipment': exercise['Equipment'],
                    'body_focus': exercise['Body Focus'],
                    'goal': exercise['Goal'],
                    'calories': exercise['Calories/10min'],
                    'skill_level': exercise['Skill Level']
                })
            
            return workout_plan
            
        except Exception as e:
            st.error(f"❌ Error generating workout: {str(e)}")
            return None

def workout_generator_ui():
    """Streamlit UI for the workout generator"""
    st.markdown("### 🎯 Quick Workout Generator")
    st.write("Get personalized workout recommendations in seconds!")
    
    # Initialize workout generator
    workout_gen = WorkoutGenerator()
    
    # Create form for user input
    with st.form("workout_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            emotion = st.selectbox(
                "How are you feeling right now?",
                options=['😴 Tired', '😌 Calm', '🎯 Focused', '💪 Energetic'],
                index=2
            )
            
            time_available = st.selectbox(
                "How much time do you have?",
                options=['15min ⚡', '30min 🕒', '45min ⏱️', '60min 🕛'],
                index=1
            )
            
        with col2:
            equipment = st.selectbox(
                "What's available around you?",
                options=['👤 Nothing', '🧘 Yoga Mat', '🏋️ Dumbbells', '💪 Bands'],
                index=0
            )
            
            need = st.selectbox(
                "What do you need most?",
                options=['⚡ Quick Energy', '😌 Stress Relief', '💪 Full Workout', '🪑 Desk Relief'],
                index=2
            )
        
        body_focus = st.selectbox(
            "Focus area?",
            options=['🔄 Full Body', '💪 Upper Body', '🦵 Lower Body', '🎯 Core', '🧘 Flexibility'],
            index=0
        )
        
        generate_clicked = st.form_submit_button("💪 Generate My Workout", use_container_width=True)
    
    # Generate and display workout
    if generate_clicked:
        with st.spinner("Creating your personalized workout..."):
            workout = workout_gen.generate_workout(emotion, time_available, equipment, need, body_focus)
            
            if workout:
                # Store workout in session state for regeneration
                st.session_state.current_workout = workout
                st.session_state.workout_params = {
                    'emotion': emotion,
                    'time_available': time_available,
                    'equipment': equipment,
                    'need': need,
                    'body_focus': body_focus
                }
                
                display_workout(workout, workout_gen)
            else:
                st.error("Could not generate a workout with the current criteria. Try adjusting your selections.")

    # Check if we have a workout in session state to allow regeneration
    if 'current_workout' in st.session_state and 'workout_params' in st.session_state:
        st.markdown("---")
        st.subheader("🔄 Not Happy With This Routine?")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Generate New Routine", use_container_width=True):
                with st.spinner("Creating a new routine..."):
                    # Generate new workout with same parameters
                    new_workout = workout_gen.generate_workout(
                        st.session_state.workout_params['emotion'],
                        st.session_state.workout_params['time_available'],
                        st.session_state.workout_params['equipment'],
                        st.session_state.workout_params['need'],
                        st.session_state.workout_params['body_focus']
                    )
                    if new_workout:
                        st.session_state.current_workout = new_workout
                        st.rerun()
        
        with col2:
            if st.button("📝 Modify Parameters", use_container_width=True):
                # Clear current workout to show form again
                if 'current_workout' in st.session_state:
                    del st.session_state.current_workout
                st.rerun()

def display_workout(workout, workout_gen):
    """Display the workout plan with enhanced information"""
    # Display workout plan
    st.success(f"### {workout['filters_applied']['body_focus']} {workout['total_time']}min Workout")
    
    # Workout summary
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Rounds", workout['rounds'])
    with col2:
        st.metric("Exercises", len(workout['exercises']))
    with col3:
        st.metric("Total Time", f"{workout['total_time']} min")
    with col4:
        categories = set(ex['category'] for ex in workout['exercises'])
        st.metric("Exercise Types", len(categories))
    
    # Exercise list with enhanced information
    st.markdown("#### 🏋️ Your Workout Plan")
    st.markdown(f"**Complete {workout['rounds']} rounds** • Rest 30-60 seconds between exercises")
    
    for i, exercise in enumerate(workout['exercises'], 1):
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{i}. {exercise['name']}**")
                st.caption(f"🏷️ {exercise['category']} • ⚡ {exercise['intensity']} Intensity")
                st.caption(f"🎯 Focus: {exercise['body_focus']}")
                st.caption(f"📊 Goal: {exercise['goal']} • 🎓 Level: {exercise['skill_level']}")
            with col2:
                st.info(exercise['sets_reps'])
            with col3:
                st.success(f"🔥 {exercise['calories']} cal/10min")
            st.divider()
    
    # Workout statistics
    with st.expander("📊 Workout Statistics"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Exercise Distribution:**")
            category_count = {}
            for exercise in workout['exercises']:
                category = exercise['category']
                category_count[category] = category_count.get(category, 0) + 1
            
            for category, count in category_count.items():
                st.write(f"• {category}: {count} exercises")
        
        with col2:
            st.write("**Intensity Levels:**")
            intensity_count = {}
            for exercise in workout['exercises']:
                intensity = exercise['intensity']
                intensity_count[intensity] = intensity_count.get(intensity, 0) + 1
            
            for intensity, count in intensity_count.items():
                st.write(f"• {intensity}: {count} exercises")
    
    # Download option
    workout_text = f"{workout['filters_applied']['body_focus']} {workout['total_time']}min Workout\n\n"
    workout_text += f"Complete {workout['rounds']} rounds:\n\n"
    for i, exercise in enumerate(workout['exercises'], 1):
        workout_text += f"{i}. {exercise['name']}\n"
        workout_text += f"   - Sets/Reps: {exercise['sets_reps']}\n"
        workout_text += f"   - Category: {exercise['category']}\n"
        workout_text += f"   - Intensity: {exercise['intensity']}\n"
        workout_text += f"   - Equipment: {exercise['equipment']}\n"
        workout_text += f"   - Calories: {exercise['calories']} cal/10min\n\n"
    
    st.download_button(
        label="📥 Download Workout Plan",
        data=workout_text,
        file_name=f"workout_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
        mime="text/plain",
        use_container_width=True
    )

# Add this to make the UI available
if __name__ == "__main__":
    workout_generator_ui()