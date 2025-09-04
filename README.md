# 🚜 লাঙল - কৃষকের ডিজিটাল হাতিয়ার

<div align="center">

<img src="logo.png" alt="লাঙল লোগো" width="100">

**🤖 Automated HTML to Google Forms Converter**

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![Google Forms API](https://img.shields.io/badge/Google%20Forms-API%20v1-green.svg)](https://developers.google.com/forms)
[![Bengali Support](https://img.shields.io/badge/Language-Bengali-red.svg)](#)

[🌐 Live Demo](https://10maruf.github.io/Langal-Stakeholder-Survey/) • [📋 Live Forms](#-live-google-forms)

</div>

---

## 🎯 কি করে?

**একটি Python script যা HTML forms কে স্বয়ংক্রিয়ভাবে Google Forms এ রূপান্তর করে।**

✨ **Zero manual work!** - শুধু script চালান, Google Forms তৈরি হয়ে যাবে।

## 🔗 Live Google Forms

আমাদের script দিয়ে তৈরি করা 6টি forms (45 questions):

| ফর্মের নাম | প্রশ্ন | লিঙ্ক |
|------------|------|------|
| **উপজেলা কৃষি কর্মকর্তা** | 4 | [Fill Form](https://forms.gle/kSiX3a97PfUbBP888) |
| **বাজার নিয়ন্ত্রণ পরিচালক** | 5 | [Fill Form](https://forms.gle/s8Rs2AmFDLFWWT2i8) |
| **কৃষি সম্প্রসারণ কর্মকর্তা** | 3 | [Fill Form](https://forms.gle/v4qhyWpyXagaMTgN8) |
| **কৃষক জরিপ** | 17 | [Fill Form](https://forms.gle/iCSB2Xzm5cdBXNx96) |
| **ক্রেতা তথ্য ও মতামত** | 8 | [Fill Form](https://forms.gle/QVKnav3tLY7BRzqU7) |
| **কৃষিবিদ জরিপ** | 8 | [Fill Form](https://forms.gle/2jNbiBwcsszyhLBJ8) |

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/10Maruf/Langal-Stakeholder-Survey.git
cd Langal-Stakeholder-Survey
python setup.py
```

### 2. Google API Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project & enable Google Forms API
3. Create OAuth 2.0 Desktop credentials
4. Download as `credentials.json`
5. Add your email as test user

### 3. Run
```bash
python ultimate_html_to_google_form_converter.py
```

## 📁 What's Inside

```
📂 old-forms/          # Original HTML forms (6 files)
🚀 converter.py         # Main automation script  
🌐 index.html          # Web interface
📖 README.md           # This file
```

## ✨ Features

| Feature | Status |
|---------|--------|
| 🤖 **Full Automation** | ✅ Zero manual work |
| 📝 **Bengali Support** | ✅ Perfect text preservation |
| 🔢 **Smart Ordering** | ✅ Questions in sequence (১,২,৩...) |
| ✅ **All Form Types** | ✅ Radio, Checkbox, Text, etc. |
| 🎯 **Other Options** | ✅ Proper "অন্যান্য" handling |
| 🚀 **Batch Process** | ✅ Convert multiple forms at once |

## 🛠️ How It Works

```
HTML Files → Python Parser → Google Forms API → Live Forms
```

1. **Scans** HTML files in `old-forms/`
2. **Extracts** questions, options, form structure
3. **Converts** Bengali numbers & orders questions
4. **Creates** Google Forms automatically via API
5. **Returns** shareable form links

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| `credentials.json not found` | Download from Google Cloud Console |
| `access_denied error` | Add your email as test user |
| `API quota exceeded` | Wait 24 hours |

## 📊 Results

- **✅ 100% Success Rate** - All 6 forms converted
- **⚡ 30 seconds** - Average conversion time per form
- **🎯 45/45 Questions** - All questions preserved
- **🔥 Zero Errors** - Perfect API integration

## 🤝 Contributing

1. Fork the repo
2. Create feature branch
3. Make changes
4. Submit pull request

## 📄 License

MIT License - Use freely for any purpose.

---

<div align="center">

**🚜 Made with ❤️ for Bengali Farmers**

**Star ⭐ this repo if it helped you!**

</div>
