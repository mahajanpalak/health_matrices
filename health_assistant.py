# health_assistant.py
import streamlit as st
import re
from datetime import datetime
import random

class HealthAssistantChatbot:
    """
    AI Health Assistant for Health Matrices Pro
    Provides personalized health guidance and support
    """
    
    def __init__(self):
        """Initialize the health assistant chatbot"""
        self.greeting_patterns = self._initialize_greeting_patterns()
        self.health_patterns = self._initialize_health_patterns()
        self.nutrition_patterns = self._initialize_nutrition_patterns()
        self.exercise_patterns = self._initialize_exercise_patterns()
        self.general_patterns = self._initialize_general_patterns()
        
    def _initialize_greeting_patterns(self):
        """Initialize greeting patterns"""
        return [
            r'\b(hi|hello|hey|greetings|howdy|hola)\b',
            r'\bgood (morning|afternoon|evening|day)\b',
            r'\bhow are you\b',
            r'\bwhats up\b',
            r"\bwhat's up\b"
        ]
    
    def _initialize_health_patterns(self):
        """Initialize health-related patterns"""
        return {
            'tired': [
                r'\b(tired|fatigue|exhausted|sleepy|low energy)\b',
                r'\bfeel (tired|exhausted|sleepy)\b',
                r'\bno energy\b',
                r'\bwhy am i so tired\b'
            ],
            'stress': [
                r'\b(stress|stressed|anxiety|anxious|worried|overwhelmed)\b',
                r'\bfeel (stress|anxiety|overwhelmed)\b',
                r'\bhow to (reduce|manage) stress\b',
                r'\bcalm (down|myself)\b'
            ],
            'sleep': [
                r'\b(sleep|insomnia|sleepless|can\'t sleep)\b',
                r'\bimprove sleep\b',
                r'\bsleep (quality|better)\b',
                r'\bwake up (tired|exhausted)\b'
            ],
            'pain': [
                r'\b(pain|hurt|aching|sore|uncomfortable)\b',
                r'\b(my|back|neck|head|joint) hurt\b',
                r'\bfeel pain\b'
            ]
        }
    
    def _initialize_nutrition_patterns(self):
        """Initialize nutrition patterns"""
        return {
            'breakfast': [
                r'\b(breakfast|morning meal)\b',
                r'\bwhat (should|can) i eat (for breakfast|in the morning)\b',
                r'\bhealthy breakfast\b'
            ],
            'lunch': [
                r'\b(lunch|midday meal)\b',
                r'\bwhat (should|can) i eat for lunch\b',
                r'\bhealthy lunch\b'
            ],
            'dinner': [
                r'\b(dinner|evening meal|supper)\b',
                r'\bwhat (should|can) i eat for dinner\b',
                r'\bhealthy dinner\b'
            ],
            'snacks': [
                r'\b(snack|hungry between meals)\b',
                r'\bhealthy snack\b',
                r'\bwhat to eat when hungry\b'
            ],
            'weight_loss': [
                r'\b(lose weight|weight loss|slim down)\b',
                r'\bhow to lose weight\b',
                r'\bburn fat\b'
            ],
            'weight_gain': [
                r'\b(gain weight|bulk up|build muscle)\b',
                r'\bhow to gain weight\b'
            ]
        }
    
    def _initialize_exercise_patterns(self):
        """Initialize exercise patterns"""
        return {
            'cardio': [
                r'\b(cardio|running|jogging|cycling|swimming)\b',
                r'\baerobic exercise\b',
                r'\bheart (rate|health)\b'
            ],
            'strength': [
                r'\b(strength|weights|lifting|muscle|resistance)\b',
                r'\bbuild muscle\b',
                r'\bweight training\b'
            ],
            'flexibility': [
                r'\b(flexibility|stretching|yoga|pilates)\b',
                r'\bbecome (more )?flexible\b'
            ],
            'beginner': [
                r'\b(beginner|starting out|new to exercise)\b',
                r'\bhow to start (exercising|working out)\b'
            ]
        }
    
    def _initialize_general_patterns(self):
        """Initialize general health patterns"""
        return {
            'motivation': [
                r'\b(motivation|motivated|unmotivated|lazy)\b',
                r'\bstay motivated\b',
                r'\bhow to (start|begin)\b'
            ],
            'progress': [
                r'\b(progress|results|improvement)\b',
                r'\bnot seeing results\b',
                r'\bwhen will i see results\b'
            ],
            'hydration': [
                r'\b(water|hydration|hydrated|dehydrated)\b',
                r'\bhow much water\b',
                r'\bdrink water\b'
            ]
        }
    
    def get_initial_greeting(self):
        """Get initial greeting when chatbot opens"""
        greetings = [
            "👋 **Hello! I'm your Health Assistant!**\n\nI'm here to provide personalized health guidance, answer your questions, and help you achieve your wellness goals.\n\n💡 You can ask me about:\n• Nutrition and meal planning\n• Exercise recommendations\n• Sleep and stress management\n• General health questions\n• Motivation and progress tracking\n\nWhat's on your mind today?",
            
            "🌟 **Welcome to your Health Assistant!**\n\nI'm your AI companion for all things health and wellness. Whether you need exercise advice, nutrition tips, or general health guidance, I'm here to help!\n\n🎯 Try asking:\n• 'I'm feeling tired, what should I do?'\n• 'What's a healthy breakfast option?'\n• 'How can I reduce stress?'\n• 'Best exercises for beginners?'\n\nHow can I assist you with your health journey today?",
            
            "💪 **Hello! Ready to boost your health?**\n\nI'm your personal Health Assistant, here to support your wellness journey with evidence-based advice and personalized recommendations.\n\n📚 I can help with:\n• Diet and nutrition planning\n• Workout routines\n• Lifestyle improvements\n• Health concerns\n• Progress tracking\n\nWhat would you like to discuss?"
        ]
        
        return random.choice(greetings)
    
    def is_greeting(self, message):
        """Check if message is a greeting"""
        message = message.lower()
        for pattern in self.greeting_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return True
        return False
    
    def get_greeting_response(self):
        """Generate greeting response"""
        responses = [
            "Hello! 😊 How can I help you with your health and wellness today?",
            "Hi there! 👋 What health questions can I answer for you?",
            "Hey! 🌟 Ready to work on your health goals? What would you like to know?",
            "Greetings! 💪 How can I assist with your fitness and nutrition today?"
        ]
        return random.choice(responses)
    
    def analyze_health_intent(self, message):
        """Analyze user message for health-related intents"""
        message_lower = message.lower()
        
        # Check health patterns
        for category, patterns in self.health_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    return category, 'health'
        
        # Check nutrition patterns
        for category, patterns in self.nutrition_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    return category, 'nutrition'
        
        # Check exercise patterns
        for category, patterns in self.exercise_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    return category, 'exercise'
        
        # Check general patterns
        for category, patterns in self.general_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    return category, 'general'
        
        return None, 'unknown'
    
    def get_health_response(self, category, user_data=None):
        """Generate health-related responses"""
        responses = {
            'tired': [
                "😴 **Feeling tired?** Here are some suggestions:\n\n• **Hydrate**: Drink 2-3 glasses of water\n• **Move**: Take a 10-minute walk or do light stretching\n• **Nutrition**: Eat a balanced snack with protein and complex carbs\n• **Rest**: Consider a 20-minute power nap if possible\n• **Check sleep**: Aim for 7-9 hours of quality sleep nightly",
                
                "💤 **Low energy levels?** Try these:\n\n• **Deep breathing**: 5 minutes of focused breathing\n• **Hydration**: Often fatigue is related to dehydration\n• **Blood sugar**: Eat a small, balanced meal\n• **Posture check**: Sit up straight for better oxygen flow\n• **Short break**: Step away from screens for 10 minutes"
            ],
            'stress': [
                "🧘 **Stress management techniques:**\n\n• **4-7-8 breathing**: Inhale 4s, hold 7s, exhale 8s\n• **Progressive relaxation**: Tense and relax muscle groups\n• **Mindful walk**: 10-minute walk focusing on surroundings\n• **Gratitude journal**: Write 3 things you're grateful for\n• **Digital detox**: 30 minutes away from devices",
                
                "🌿 **To reduce stress:**\n\n• **Box breathing**: 4s in, 4s hold, 4s out, 4s hold\n• **Gentle stretching**: 5-10 minutes of light yoga\n• **Herbal tea**: Chamomile or lavender tea can help\n• **Nature break**: Spend 15 minutes outdoors\n• **Music therapy**: Listen to calming music"
            ],
            'sleep': [
                "🌙 **Improve sleep quality:**\n\n• **Consistent schedule**: Same bedtime/waketime daily\n• **Dark environment**: Use blackout curtains\n• **Cool temperature**: 18-20°C (65-68°F) ideal\n• **No screens**: 1 hour before bed\n• **Relaxing routine**: Reading, meditation, warm bath",
                
                "💤 **Better sleep habits:**\n\n• **Caffeine cutoff**: No caffeine after 2 PM\n• **Evening light**: Dim lights 2 hours before bed\n• **Bedroom only**: Use bed only for sleep and intimacy\n• **Wind down**: 30-minute pre-sleep routine\n• **White noise**: Use if noise is an issue"
            ],
            'pain': [
                "🩹 **For general discomfort:**\n\n• **Gentle movement**: Light stretching if appropriate\n• **Heat/cold**: Use based on type of pain\n• **Proper posture**: Check sitting/standing alignment\n• **Hydration**: Drink plenty of water\n• **Rest**: Allow affected area to recover\n\n⚠️ *Consult healthcare provider for persistent pain*",
                
                "💊 **Pain management tips:**\n\n• **Movement breaks**: Change positions regularly\n• **Mindfulness**: Focus on breathing through discomfort\n• **Anti-inflammatory foods**: Turmeric, ginger, omega-3s\n• **Proper ergonomics**: Adjust workspace setup\n• **Professional advice**: See doctor if pain continues"
            ]
        }
        
        return random.choice(responses.get(category, ["I understand you're dealing with health concerns. For personalized advice, consider consulting with a healthcare professional."]))
    
    def get_nutrition_response(self, category, user_data=None):
        """Generate nutrition-related responses"""
        responses = {
            'breakfast': [
                "🍳 **Healthy breakfast options:**\n\n• **Protein smoothie**: Greek yogurt, berries, spinach, protein powder\n• **Oatmeal**: Oats with nuts, seeds, and fruit\n• **Eggs**: Scrambled with vegetables\n• **Avocado toast**: Whole grain bread with avocado and eggs\n• **Chia pudding**: Chia seeds with almond milk and berries",
                
                "🌅 **Nutritious morning meals:**\n\n• **Greek yogurt**: With granola and honey\n• **Whole grain toast**: With peanut butter and banana\n• **Breakfast burrito**: Whole wheat tortilla with eggs and veggies\n• **Cottage cheese**: With fruit and nuts\n• **Protein pancakes**: With berries and Greek yogurt"
            ],
            'lunch': [
                "🥗 **Balanced lunch ideas:**\n\n• **Quinoa bowl**: With roasted vegetables and chicken/fish\n• **Large salad**: Greens, protein, healthy fats, complex carbs\n• **Wrap**: Whole grain wrap with lean protein and veggies\n• **Soup**: Vegetable or lentil soup with whole grain bread\n• **Buddha bowl**: Grains, protein, vegetables, sauce",
                
                "🍱 **Healthy midday meals:**\n\n• **Stir-fry**: Lots of vegetables with tofu/chicken and brown rice\n• **Sandwich**: Whole grain bread with lean protein and vegetables\n• **Leftovers**: Dinner leftovers make great lunches\n• **Grain salad**: Farro or barley with vegetables and dressing\n• **Protein box**: Hard-boiled eggs, cheese, nuts, fruits"
            ],
            'dinner': [
                "🍲 **Nutritious dinner options:**\n\n• **Grilled fish**: With roasted vegetables and quinoa\n• **Chicken**: Baked with sweet potato and broccoli\n• **Vegetable curry**: With chickpeas and brown rice\n• **Turkey chili**: With beans and vegetables\n• **Stuffed peppers**: With lean ground meat and quinoa",
                
                "🍽️ **Evening meal ideas:**\n\n• **Salmon**: With asparagus and wild rice\n• **Lean steak**: With mushroom sauce and roasted potatoes\n• **Vegetable pasta**: Whole wheat pasta with tomato sauce and vegetables\n• **Stir-fry**: Protein with lots of colorful vegetables\n• **Sheet pan meal**: Protein and vegetables roasted together"
            ],
            'snacks': [
                "🍎 **Healthy snack options:**\n\n• **Apple slices**: With almond butter\n• **Greek yogurt**: With berries and honey\n• **Vegetable sticks**: With hummus\n• **Handful of nuts**: Almonds or walnuts\n• **Hard-boiled eggs**: With sprinkle of salt\n• **Rice cakes**: With avocado or peanut butter",
                
                "🥜 **Smart snacking:**\n\n• **Cottage cheese**: With pineapple\n• **Protein bar**: Look for low-sugar options\n• **Edamame**: Steamed with sea salt\n• **Dark chocolate**: 70% cocoa or higher\n• **Trail mix**: Nuts, seeds, dried fruit\n• **Celery**: With peanut butter and raisins"
            ],
            'weight_loss': [
                "⚖️ **Weight loss nutrition tips:**\n\n• **Protein focus**: Include protein in every meal\n• **Fiber rich**: Lots of vegetables and whole grains\n• **Portion control**: Use smaller plates\n• **Mindful eating**: Eat slowly without distractions\n• **Hydration**: Drink water before meals\n• **Limit processed**: Focus on whole foods",
                
                "🏃 **Nutrition for weight loss:**\n\n• **Calorie deficit**: Eat slightly less than you burn\n• **Balanced meals**: Protein + veggies + healthy fats\n• **Regular meals**: Don't skip meals\n• **Smart swaps**: Greek yogurt instead of sour cream\n• **Plan ahead**: Prepare healthy snacks\n• **Track intake**: Use app to monitor calories"
            ],
            'weight_gain': [
                "💪 **Healthy weight gain strategies:**\n\n• **Calorie surplus**: Eat more than you burn\n• **Protein focus**: 1.6-2.2g protein per kg body weight\n• **Frequent meals**: 3 main meals + 2-3 snacks\n• **Calorie-dense foods**: Nuts, nut butters, avocados\n• **Strength training**: Build muscle mass\n• **Liquid calories**: Smoothies, milk, protein shakes",
                
                "📈 **Building mass nutrition:**\n\n• **Quality calories**: Nutrient-dense foods, not junk\n• **Post-workout nutrition**: Protein and carbs within 2 hours\n• **Healthy fats**: Olive oil, nuts, seeds, avocados\n• **Complex carbs**: Oats, sweet potatoes, brown rice\n• **Consistency**: Eat regularly throughout the day"
            ]
        }
        
        return random.choice(responses.get(category, ["I'd be happy to help with nutrition advice! Could you provide more details about your dietary needs?"]))
    
    def get_exercise_response(self, category, user_data=None):
        """Generate exercise-related responses"""
        responses = {
            'cardio': [
                "🏃 **Cardio exercise recommendations:**\n\n• **Walking**: 30-60 minutes daily\n• **Running**: 20-30 minutes, 3-4 times weekly\n• **Cycling**: 30-45 minutes, moderate intensity\n• **Swimming**: 30 minutes, full-body workout\n• **HIIT**: 20-30 minutes, high intensity intervals\n• **Dancing**: 30 minutes, fun cardio option",
                
                "❤️ **Cardiovascular health:**\n\n• **Brisk walking**: 150 minutes weekly minimum\n• **Interval training**: 1:1 work:rest ratio\n• **Stair climbing**: Great for leg strength and cardio\n• **Jump rope**: 10-15 minutes, high intensity\n• **Rowing**: Full-body cardio workout\n• **Group classes**: Spin, aerobics, dance"
            ],
            'strength': [
                "💪 **Strength training basics:**\n\n• **Compound movements**: Squats, deadlifts, bench press\n• **Frequency**: 2-3 times weekly per muscle group\n• **Progressive overload**: Gradually increase weight/reps\n• **Form focus**: Proper technique prevents injury\n• **Rest periods**: 60-90 seconds between sets\n• **Full body**: Work all major muscle groups",
                
                "🏋️ **Building strength:**\n\n• **Bodyweight exercises**: Push-ups, pull-ups, squats\n• **Free weights**: Dumbbells, barbells, kettlebells\n• **Machines**: Good for beginners, controlled movement\n• **Rep ranges**: 8-12 reps for hypertrophy\n• **Warm-up**: 5-10 minutes light cardio + dynamic stretches\n• **Cool down**: Static stretching after workout"
            ],
            'flexibility': [
                "🧘 **Flexibility and mobility:**\n\n• **Daily stretching**: 10-15 minutes daily\n• **Yoga**: 2-3 times weekly for flexibility\n• **Dynamic stretching**: Before workouts\n• **Static stretching**: After workouts or separately\n• **Foam rolling**: For muscle recovery\n• **Pilates**: Core strength and flexibility",
                
                "🤸 **Improving flexibility:**\n\n• **Hold stretches**: 30 seconds minimum\n• **Breathe deeply**: Relax into stretches\n• **Consistency**: Daily practice yields best results\n• **Warm muscles**: Stretch after light activity\n• **Full range**: Work all major muscle groups\n• **Listen to body**: Stretch to mild discomfort, not pain"
            ],
            'beginner': [
                "🚶 **Starting exercise safely:**\n\n• **Start slow**: 20-30 minutes, 3 times weekly\n• **Mix it up**: Cardio + strength + flexibility\n• **Listen to body**: Rest when needed\n• **Proper shoes**: Supportive footwear\n• **Warm up**: 5-10 minutes light activity\n• **Cool down**: Stretching after exercise",
                
                "🎯 **Beginner workout plan:**\n\n• **Week 1-2**: 20 min walk + bodyweight exercises\n• **Week 3-4**: 30 min walk + light weights\n• **Consistency**: Focus on building habit\n• **Form first**: Learn proper technique\n• **Rest days**: 1-2 days weekly for recovery\n• **Progress slowly**: Increase intensity gradually"
            ]
        }
        
        return random.choice(responses.get(category, ["I can help you with exercise recommendations! What type of workout are you interested in?"]))
    
    def get_general_response(self, category, user_data=None):
        """Generate general health responses"""
        responses = {
            'motivation': [
                "🔥 **Staying motivated:**\n\n• **Set clear goals**: Specific, measurable targets\n• **Track progress**: Journal, photos, measurements\n• **Find your why**: Connect to deeper reasons\n• **Small wins**: Celebrate daily achievements\n• **Accountability**: Workout buddy or coach\n• **Variety**: Change routines to prevent boredom",
                
                "🎯 **Building consistency:**\n\n• **Habit stacking**: Add exercise to existing routines\n• **Prepare ahead**: Lay out workout clothes night before\n• **Music motivation**: Create energizing playlists\n• **Visual reminders**: Post goals where you'll see them\n• **Start small**: 10 minutes is better than zero\n• **Progress photos**: Visual evidence of changes"
            ],
            'progress': [
                "📊 **Tracking progress:**\n\n• **Multiple metrics**: Weight, measurements, photos, strength\n• **Non-scale victories**: Energy levels, sleep quality, mood\n• **Consistency over perfection**: Regular effort matters most\n• **Plateaus are normal**: Body adapts to routines\n• **Adjust as needed**: Change workout or nutrition plan\n• **Patience**: Real changes take time",
                
                "📈 **Seeing results:**\n\n• **Realistic expectations**: 0.5-1kg weight loss weekly\n• **Strength gains**: Measure weights and reps\n• **Body composition**: Focus on fat loss, not just weight\n• **Lifestyle factors**: Sleep, stress, hydration affect results\n• **Professional assessment**: Consider body composition testing\n• **Trust the process**: Consistency brings results"
            ],
            'hydration': [
                "💧 **Hydration guidelines:**\n\n• **Daily target**: 2-3 liters for most adults\n• **Listen to thirst**: Drink when thirsty\n• **Urine color**: Pale yellow = well hydrated\n• **Exercise needs**: Extra 500-1000ml per hour of exercise\n• **Electrolytes**: Important for intense/long workouts\n• **Food sources**: Fruits and vegetables contribute to hydration",
                
                "🚰 **Staying hydrated:**\n\n• **Carry water bottle**: Visual reminder to drink\n• **Set reminders**: Phone alerts to drink water\n• **Flavor water**: Add lemon, cucumber, mint\n• **Pre-meal water**: Glass before each meal\n• **Monitor intake**: Track daily water consumption\n• **Weather adjustment**: More in hot/humid conditions"
            ]
        }
        
        return random.choice(responses.get(category, ["I'm here to support your health journey! What specific aspect would you like to discuss?"]))
    
    def get_unknown_response(self):
        """Generate response for unrecognized queries"""
        responses = [
            "🤔 I'm not sure I understand. Could you rephrase your question? I can help with:\n• Nutrition and meal planning\n• Exercise recommendations\n• Sleep and stress management\n• General health questions\n• Motivation and progress tracking",
            
            "💭 I want to make sure I give you the best advice. Could you provide more details about what you're looking for? I specialize in:\n• Diet and nutrition guidance\n• Workout plans and exercise tips\n• Lifestyle improvement strategies\n• Health and wellness questions",
            
            "🔍 I'd love to help! Could you tell me more about what health or fitness topic you're interested in? I can assist with:\n• Meal planning and food choices\n• Exercise routines and techniques\n• Sleep quality and stress reduction\n• General wellness and healthy habits"
        ]
        return random.choice(responses)
    
    def get_thanking_response(self):
        """Response to thank you messages"""
        responses = [
            "You're welcome! 😊 I'm glad I could help. Feel free to ask any other health questions!",
            "Happy to assist! 🌟 Let me know if you need any other health or fitness advice.",
            "My pleasure! 💪 I'm here whenever you need guidance on your health journey.",
            "You're very welcome! 👋 Don't hesitate to reach out with more questions."
        ]
        return random.choice(responses)
    
    def get_goodbye_response(self):
        """Response to goodbye messages"""
        responses = [
            "Goodbye! 👋 Take care of your health and feel free to come back anytime!",
            "See you later! 💪 Keep up the great work on your fitness journey!",
            "Bye for now! 🌟 Remember to stay consistent with your health goals!",
            "Take care! 😊 Come back anytime you need health advice or motivation!"
        ]
        return random.choice(responses)
    
    def process_message(self, message, user_data=None):
        """
        Process user message and generate appropriate response
        
        Args:
            message: User's input message
            user_data: Optional user profile data for personalized responses
            
        Returns:
            Dictionary with response
        """
        message = message.strip()
        
        # Check for thanking
        if re.search(r'\b(thank|thanks|appreciate)\b', message, re.IGNORECASE):
            return {
                'response': self.get_thanking_response(),
                'type': 'thanks'
            }
        
        # Check for goodbye
        if re.search(r'\b(bye|goodbye|see you|exit|quit)\b', message, re.IGNORECASE):
            return {
                'response': self.get_goodbye_response(),
                'type': 'goodbye'
            }
        
        # Check for greeting
        if self.is_greeting(message):
            return {
                'response': self.get_greeting_response(),
                'type': 'greeting'
            }
        
        # Analyze health intent
        category, intent_type = self.analyze_health_intent(message)
        
        if intent_type == 'health' and category:
            return {
                'response': self.get_health_response(category, user_data),
                'type': 'health_advice'
            }
        elif intent_type == 'nutrition' and category:
            return {
                'response': self.get_nutrition_response(category, user_data),
                'type': 'nutrition_advice'
            }
        elif intent_type == 'exercise' and category:
            return {
                'response': self.get_exercise_response(category, user_data),
                'type': 'exercise_advice'
            }
        elif intent_type == 'general' and category:
            return {
                'response': self.get_general_response(category, user_data),
                'type': 'general_advice'
            }
        else:
            return {
                'response': self.get_unknown_response(),
                'type': 'unknown'
            }


def show_health_assistant():
    """Main function to display health assistant - call this from app1.py"""
    try:
        # Clear any existing problematic session state
        if 'health_assistant' in st.session_state:
            # Check if it's a boolean (incorrectly set)
            if isinstance(st.session_state.health_assistant, bool):
                del st.session_state.health_assistant
        
        # Initialize fresh session state
        if 'health_assistant' not in st.session_state:
            st.session_state.health_assistant = HealthAssistantChatbot()
        
        if 'health_chat_history' not in st.session_state:
            st.session_state.health_chat_history = []
        
        if 'show_health_initial_greeting' not in st.session_state:
            st.session_state.show_health_initial_greeting = True
        
        # Handle initial greeting
        if (st.session_state.show_health_initial_greeting and 
            len(st.session_state.health_chat_history) == 0):
            initial_msg = st.session_state.health_assistant.get_initial_greeting()
            st.session_state.health_chat_history.append({
                'role': 'assistant',
                'content': initial_msg,
                'timestamp': datetime.now()
            })
            st.session_state.show_health_initial_greeting = False
        
        # Load user data for personalized responses
        user_data = None
        if hasattr(st.session_state, 'user_id') and st.session_state.user_id:
            try:
                from database import load_user_profile as load_user_profile_db
                user_data = load_user_profile_db(st.session_state.user_id)
            except:
                pass
        
        # Main chat container
        st.markdown("""
        <div style='background: rgba(42, 49, 66, 0.8); padding: 2rem; border-radius: 15px; border: 1px solid rgba(0, 224, 255, 0.3); margin-bottom: 2rem;'>
        """, unsafe_allow_html=True)
        
        # Chat history
        chat_container = st.container()
        with chat_container:
            # Display chat history (show last 8 messages)
            for message in st.session_state.health_chat_history[-8:]:
                if message['role'] == 'user':
                    st.markdown(f"""
                    <div style='background: rgba(0, 224, 255, 0.2); padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-left: 4px solid #00e0ff;'>
                        <div style='color: #ffffff; font-weight: 600; margin-bottom: 0.5rem;'>👤 You</div>
                        <div style='color: #e2e8f0;'>{message['content']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style='background: rgba(42, 157, 143, 0.2); padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-left: 4px solid #2a9d8f;'>
                        <div style='color: #ffffff; font-weight: 600; margin-bottom: 0.5rem;'>🤖 Health Assistant</div>
                        <div style='color: #e2e8f0; white-space: pre-wrap;'>{message['content']}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Input area
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_input(
                "Type your health question here...",
                key="health_chat_input",
                placeholder="e.g., I'm feeling tired today, what should I do? Or: What's a healthy breakfast option?",
                label_visibility="collapsed"
            )
        
        with col2:
            send_button = st.button("Send", use_container_width=True, key="health_send_button")
        
        # Process message when send button is clicked
        if send_button and user_input:
            # Add user message to history
            st.session_state.health_chat_history.append({
                'role': 'user',
                'content': user_input,
                'timestamp': datetime.now()
            })
            
            # Get assistant response
            try:
                result = st.session_state.health_assistant.process_message(user_input, user_data)
                
                # Add assistant response to history
                st.session_state.health_chat_history.append({
                    'role': 'assistant',
                    'content': result['response'],
                    'timestamp': datetime.now(),
                    'type': result['type']
                })
            except Exception as e:
                # Fallback response if processing fails
                st.session_state.health_chat_history.append({
                    'role': 'assistant',
                    'content': "I apologize, but I'm having trouble processing your request right now. Please try again.",
                    'timestamp': datetime.now(),
                    'type': 'error'
                })
            
            # Rerun to update chat
            st.rerun()
        
        # Quick questions buttons
        st.markdown("---")
        st.subheader("💡 Quick Questions")
        
        quick_questions = [
            "What should I eat for breakfast?",
            "I'm stressed, any suggestions?",
            "Best exercises for weight loss?",
            "How to improve sleep quality?",
            "I'm feeling tired, what should I do?",
            "Healthy snack ideas?",
            "How to stay motivated?"
        ]
        
        cols = st.columns(2)
        for i, question in enumerate(quick_questions):
            with cols[i % 2]:
                if st.button(question, use_container_width=True, key=f"quick_{i}"):
                    # Add quick question to chat
                    st.session_state.health_chat_history.append({
                        'role': 'user',
                        'content': question,
                        'timestamp': datetime.now()
                    })
                    
                    # Get response
                    try:
                        result = st.session_state.health_assistant.process_message(question, user_data)
                        
                        # Add response to history
                        st.session_state.health_chat_history.append({
                            'role': 'assistant',
                            'content': result['response'],
                            'timestamp': datetime.now(),
                            'type': result['type']
                        })
                    except Exception as e:
                        # Fallback response
                        st.session_state.health_chat_history.append({
                            'role': 'assistant',
                            'content': "I'm here to help with your health questions! What would you like to know?",
                            'timestamp': datetime.now(),
                            'type': 'fallback'
                        })
                    
                    st.rerun()
        
        # Clear chat button
        st.markdown("---")
        if st.button("🗑️ Clear Chat", use_container_width=True, key="clear_health_chat"):
            st.session_state.health_chat_history = []
            st.session_state.show_health_initial_greeting = True
            st.rerun()
            
    except Exception as e:
        st.error(f"Error initializing health assistant: {str(e)}")
        st.info("Please refresh the page or use the reset button below.")
        
        # Reset everything
        if st.button("🔄 Reset Health Assistant", use_container_width=True):
            keys_to_clear = ['health_assistant', 'health_chat_history', 'show_health_initial_greeting']
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()


# For backward compatibility
def render_health_assistant_interface():
    """Alias for show_health_assistant"""
    show_health_assistant()


# Standalone demo
if __name__ == "__main__":
    st.set_page_config(
        page_title="Health Assistant",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Health Assistant")
    st.markdown("---")
    
    show_health_assistant()