import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, User, Calendar, Briefcase, IndianRupee, Mic, MicOff, UserCircle } from 'lucide-react';
import { useSpeechToText } from '../hooks/useSpeechToText';
import { useTextToSpeech } from '../hooks/useTextToSpeech';
import { useVoice } from '../context/VoiceContext';

const VoiceForm = () => {
    const navigate = useNavigate();
    const { transcript, isListening, startListening, stopListening, supported } = useSpeechToText();
    const { speak } = useTextToSpeech();
    const { formData, updateField, saveSession } = useVoice();

    // State to track which field is currently receiving voice input
    const [activeField, setActiveField] = useState(null);

    useEffect(() => {
        const message = "Welcome. You can manually type your details or click the microphone icon to speak them.";
        speak(message);
    }, [speak]);

    // Update form when transcript changes
    useEffect(() => {
        if (transcript && activeField) {
            updateField(activeField, transcript);
        }
    }, [transcript, activeField, updateField]);

    const handleChange = (e) => {
        updateField(e.target.name, e.target.value);
    };

    const handleVoiceInput = (fieldName) => {
        if (isListening && activeField === fieldName) {
            stopListening();
            setActiveField(null);
        } else {
            setActiveField(fieldName);
            startListening();
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        saveSession();
        navigate('/review-application');
    };

    const fields = [
        { name: 'fullName', label: 'Full Name', icon: User, type: 'text', placeholder: "e.g. John Doe" },
        { name: 'age', label: 'Age', icon: Calendar, type: 'number', placeholder: "e.g. 25" },
        { name: 'occupation', label: 'Occupation', icon: Briefcase, type: 'text', placeholder: "e.g. Student" },
        { name: 'income', label: 'Annual Income', icon: IndianRupee, type: 'text', placeholder: "e.g. 500000" },
        { name: 'fatherName', label: "Father's Name", icon: User, type: 'text', placeholder: "e.g. Robert Doe" },
        { name: 'motherName', label: "Mother's Name", icon: User, type: 'text', placeholder: "e.g. Mary Doe" }
    ];

    return (
        <div className="min-h-screen bg-transparent text-white flex flex-col items-center justify-center p-4 relative overflow-hidden">
            {/* Background Decoration matching Home.jsx */}
            <div className="fixed inset-0 z-0 bg-mesh pointer-events-none opacity-20"></div>
            <div className="auth-background">
                <div className="gradient-orb gradient-orb-1 opacity-20"></div>
                <div className="gradient-orb opacity-10" style={{ top: '40%', left: '10%', width: '300px', height: '300px', background: 'cyan' }}></div>
            </div>

            <div className="relative z-10 w-full max-w-4xl glass-panel p-8 rounded-3xl shadow-[0_0_40px_rgba(0,0,0,0.5)] border border-white/10 backdrop-blur-xl">
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center p-3 bg-primary/10 rounded-full mb-4 text-primary animate-pulse">
                        <UserCircle size={32} />
                    </div>
                    <h2 className="text-3xl font-black tracking-tight">Personal <span className="text-primary">Information</span></h2>
                    <p className="text-slate-400 text-sm mt-2">Use your voice to fill out the form below. Click the microphone icon next to each field.</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Left Column */}
                        <div className="space-y-5">
                            {[
                                { name: 'fullName', label: 'Full Name', icon: User, type: 'text', placeholder: "e.g. raju" },
                                { name: 'fatherName', label: "Father's Name", icon: User, type: 'text', placeholder: "e.g. murugan" },
                                { name: 'motherName', label: "Mother's Name", icon: User, type: 'text', placeholder: "e.g. jothi" }
                            ].map((field) => (
                                <div key={field.name} className="group">
                                    <label className="block text-xs font-bold text-primary uppercase tracking-wider mb-1.5 ml-1">{field.label}</label>
                                    <div className="relative flex items-center gap-2">
                                        <div className="relative flex-1 group-focus-within:text-primary transition-colors">
                                            <field.icon className="absolute left-3 top-3.5 text-slate-500 group-focus-within:text-primary w-5 h-5 transition-colors" />
                                            <input
                                                type={field.type}
                                                name={field.name}
                                                value={formData[field.name]}
                                                onChange={handleChange}
                                                placeholder={field.placeholder}
                                                className="w-full bg-slate-900/50 border border-white/10 rounded-xl py-3 pl-10 pr-4 focus:ring-2 focus:ring-primary/50 focus:border-primary focus:bg-slate-900 outline-none text-white transition-all hover:border-white/20"
                                                required
                                            />
                                        </div>
                                        {/* Mic Button */}
                                        {supported && (
                                            <button
                                                type="button"
                                                onClick={() => handleVoiceInput(field.name)}
                                                className={`p-3 rounded-xl border transition-all ${activeField === field.name && isListening
                                                    ? 'bg-red-500/20 text-red-500 border-red-500 animate-pulse'
                                                    : 'bg-white/5 text-slate-400 border-white/10 hover:text-primary hover:border-primary'
                                                    }`}
                                                title="Click to Speak"
                                            >
                                                {activeField === field.name && isListening ? <MicOff size={20} /> : <Mic size={20} />}
                                            </button>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* Right Column */}
                        <div className="space-y-5">
                            {/* Age & Income - Standard Inputs */}
                            {[
                                { name: 'age', label: 'Age', icon: Calendar, type: 'number', placeholder: "e.g. 25" },
                                { name: 'income', label: 'Annual Income', icon: IndianRupee, type: 'text', placeholder: "e.g. 500000" }
                            ].map((field) => (
                                <div key={field.name} className="group">
                                    <label className="block text-xs font-bold text-primary uppercase tracking-wider mb-1.5 ml-1">{field.label}</label>
                                    <div className="relative flex items-center gap-2">
                                        <div className="relative flex-1 group-focus-within:text-primary transition-colors">
                                            <field.icon className="absolute left-3 top-3.5 text-slate-500 group-focus-within:text-primary w-5 h-5 transition-colors" />
                                            <input
                                                type={field.type}
                                                name={field.name}
                                                value={formData[field.name]}
                                                onChange={handleChange}
                                                placeholder={field.placeholder}
                                                className="w-full bg-slate-900/50 border border-white/10 rounded-xl py-3 pl-10 pr-4 focus:ring-2 focus:ring-primary/50 focus:border-primary focus:bg-slate-900 outline-none text-white transition-all hover:border-white/20"
                                                required
                                            />
                                        </div>
                                        {/* Mic Button */}
                                        {supported && (
                                            <button
                                                type="button"
                                                onClick={() => handleVoiceInput(field.name)}
                                                className={`p-3 rounded-xl border transition-all ${activeField === field.name && isListening
                                                    ? 'bg-red-500/20 text-red-500 border-red-500 animate-pulse'
                                                    : 'bg-white/5 text-slate-400 border-white/10 hover:text-primary hover:border-primary'
                                                    }`}
                                                title="Click to Speak"
                                            >
                                                {activeField === field.name && isListening ? <MicOff size={20} /> : <Mic size={20} />}
                                            </button>
                                        )}
                                    </div>
                                </div>
                            ))}

                            {/* Occupation - Dropdown */}
                            <div className="group">
                                <label className="block text-xs font-bold text-primary uppercase tracking-wider mb-1.5 ml-1">Occupation</label>
                                <div className="relative flex items-center gap-2">
                                    <div className="relative flex-1 group-focus-within:text-primary transition-colors">
                                        <Briefcase className="absolute left-3 top-3.5 text-slate-500 group-focus-within:text-primary w-5 h-5 transition-colors" />
                                        <select
                                            name="occupation"
                                            value={formData.occupation}
                                            onChange={handleChange}
                                            className="w-full bg-slate-900/50 border border-white/10 rounded-xl py-3 pl-10 pr-4 focus:ring-2 focus:ring-primary/50 focus:border-primary focus:bg-slate-900 outline-none text-white transition-all hover:border-white/20 appearance-none cursor-pointer"
                                            required
                                        >
                                            <option value="" disabled className="bg-slate-900 text-slate-400">Select Occupation</option>
                                            <option value="student" className="bg-slate-900">Student</option>
                                            <option value="unemployed" className="bg-slate-900">Unemployed</option>
                                            <option value="employed" className="bg-slate-900">Employed</option>
                                            <option value="business" className="bg-slate-900">Business</option>
                                            <option value="farmer" className="bg-slate-900">Farmer</option>
                                            <option value="retired" className="bg-slate-900">Retired</option>
                                            <option value="other" className="bg-slate-900">Other</option>
                                        </select>
                                    </div>
                                    {/* Mic Button for Occupation (Optional - can set value if spoken word matches option) */}
                                    {supported && (
                                        <button
                                            type="button"
                                            onClick={() => handleVoiceInput('occupation')}
                                            className={`p-3 rounded-xl border transition-all ${activeField === 'occupation' && isListening
                                                ? 'bg-red-500/20 text-red-500 border-red-500 animate-pulse'
                                                : 'bg-white/5 text-slate-400 border-white/10 hover:text-primary hover:border-primary'
                                                }`}
                                            title="Click to Speak"
                                        >
                                            {activeField === 'occupation' && isListening ? <MicOff size={20} /> : <Mic size={20} />}
                                        </button>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>

                    <button
                        type="submit"
                        className="w-full bg-primary text-background-dark font-bold py-4 rounded-xl hover:brightness-110 transition-all flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(0,234,255,0.4)] hover:shadow-[0_0_30px_rgba(0,234,255,0.6)] hover:-translate-y-1 transform duration-200 mt-2"
                    >
                        <span>Next Step</span>
                        <ArrowRight size={20} />
                    </button>

                    <button
                        type="button"
                        onClick={() => navigate('/')}
                        className="w-full mt-4 text-slate-500 hover:text-white text-sm font-medium transition-colors"
                    >
                        Cancel & Return Home
                    </button>
                </form>
            </div>
        </div>
    );
};

export default VoiceForm;
