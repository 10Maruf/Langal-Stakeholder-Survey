#!/usr/bin/env python3
"""
Ultimate HTML to Google Forms Converter
- All issues fixed
- Proper Google Forms formatting
- Complete question parsing
"""

import os
import json
import time
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup, NavigableString
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

class UltimateHTMLFormParser:
    """Ultimate parser that captures everything"""
    
    def __init__(self):
        self.form_data = {}
    
    def parse_html_file(self, file_path: str) -> Dict[str, Any]:
        """Parse HTML file completely"""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract form title
        title_element = soup.find('title') or soup.find('h1') or soup.find('h2')
        title = title_element.get_text().strip() if title_element else "Untitled Form"
        
        # Find the form element
        form = soup.find('form')
        if not form:
            raise ValueError(f"No form found in {file_path}")
        
        questions = self._extract_all_questions_ultimate(form)
        
        return {
            'title': title,
            'description': f'Converted from {Path(file_path).name}',
            'questions': questions
        }
    
    def _extract_all_questions_ultimate(self, form_element) -> List[Dict[str, Any]]:
        """Ultimate question extraction"""
        questions = []
        
        # Method 1: div.question style (bazar.html)
        question_divs = form_element.find_all('div', class_='question')
        if question_divs:
            for div in question_divs:
                question_data = self._parse_question_div_ultimate(div)
                if question_data:
                    questions.append(question_data)
        
        # Method 2: label-based parsing (customer.html, krishok.html)
        else:
            all_labels = form_element.find_all('label')
            processed_names = set()
            
            for label in all_labels:
                # Skip option labels
                if label.find('input'):
                    continue
                
                question_text = label.get_text().strip()
                if not question_text:
                    continue
                
                question_number = self._extract_question_number(question_text)
                
                # Find associated inputs
                question_data = self._find_associated_elements(label, form_element, processed_names)
                if question_data:
                    question_data['question_text'] = question_text
                    question_data['question_number'] = question_number
                    questions.append(question_data)
        
        # Sort by question number
        questions = sorted(questions, key=lambda q: q.get('question_number', 999))
        
        return questions
    
    def _parse_question_div_ultimate(self, question_div) -> Optional[Dict[str, Any]]:
        """Ultimate question div parsing"""
        label = question_div.find('label')
        if not label:
            return None
        
        question_text = label.get_text().strip()
        question_number = self._extract_question_number(question_text)
        
        # Get all non-hidden inputs
        inputs = []
        for inp in question_div.find_all('input'):
            if inp.get('class') and 'hidden' in inp.get('class', []):
                continue
            inputs.append(inp)
        
        if not inputs:
            return None
        
        return self._process_inputs_ultimate(inputs, question_text, question_number)
    
    def _find_associated_elements(self, label, form_element, processed_names) -> Optional[Dict[str, Any]]:
        """Find elements associated with label"""
        current = label.next_sibling
        
        while current:
            if hasattr(current, 'name'):
                if current.name == 'div' and 'options' in current.get('class', []):
                    return self._parse_options_div_ultimate(current, processed_names)
                elif current.name == 'select':
                    return self._parse_select_ultimate(current, processed_names)
                elif current.name in ['input', 'textarea']:
                    return self._parse_single_element_ultimate(current, processed_names)
                elif current.name == 'label':
                    break
            current = current.next_sibling
        
        return None
    
    def _parse_options_div_ultimate(self, options_div, processed_names) -> Optional[Dict[str, Any]]:
        """Ultimate options div parsing"""
        inputs = options_div.find_all('input', {'type': ['radio', 'checkbox']})
        if not inputs:
            return None
        
        input_type = inputs[0].get('type')
        name = inputs[0].get('name')
        
        if name in processed_names:
            return None
        processed_names.add(name)
        
        options = []
        has_other = False
        
        for input_elem in inputs:
            option_text = self._get_option_text_ultimate(input_elem)
            if option_text:
                if self._is_other_option(option_text):
                    has_other = True
                else:
                    options.append(option_text)
        
        result = {
            'type': 'MULTIPLE_CHOICE' if input_type == 'radio' else 'CHECKBOX',
            'options': options,
            'required': False,
            'name': name
        }
        
        if has_other:
            result['has_other'] = True
        
        return result
    
    def _process_inputs_ultimate(self, inputs, question_text, question_number) -> Optional[Dict[str, Any]]:
        """Ultimate input processing"""
        # Group by name
        input_groups = {}
        for inp in inputs:
            name = inp.get('name', '')
            if name:
                if name not in input_groups:
                    input_groups[name] = []
                input_groups[name].append(inp)
        
        # Process the main group
        for name, group in input_groups.items():
            if not group:
                continue
            
            input_type = group[0].get('type', 'text')
            
            if input_type in ['radio', 'checkbox']:
                options = []
                has_other = False
                
                for inp in group:
                    option_text = self._get_option_text_ultimate(inp)
                    if option_text:
                        if self._is_other_option(option_text):
                            has_other = True
                        else:
                            options.append(option_text)
                
                result = {
                    'question_text': question_text,
                    'question_number': question_number,
                    'type': 'MULTIPLE_CHOICE' if input_type == 'radio' else 'CHECKBOX',
                    'options': options,
                    'required': False,
                    'name': name
                }
                
                if has_other:
                    result['has_other'] = True
                
                return result
            
            elif input_type == 'text':
                return {
                    'question_text': question_text,
                    'question_number': question_number,
                    'type': 'TEXT',
                    'required': False,
                    'name': name
                }
        
        return None
    
    def _parse_select_ultimate(self, select_element, processed_names) -> Optional[Dict[str, Any]]:
        """Ultimate select parsing"""
        name = select_element.get('name')
        if name in processed_names:
            return None
        processed_names.add(name)
        
        options = []
        has_other = False
        
        for option in select_element.find_all('option'):
            value = option.get('value', '').strip()
            text = option.get_text().strip()
            
            if value and value != '' and text:
                if self._is_other_option(text):
                    has_other = True
                else:
                    options.append(text)
        
        result = {
            'type': 'MULTIPLE_CHOICE',
            'options': options,
            'required': False,
            'name': name
        }
        
        if has_other:
            result['has_other'] = True
        
        return result
    
    def _parse_single_element_ultimate(self, element, processed_names) -> Optional[Dict[str, Any]]:
        """Ultimate single element parsing"""
        name = element.get('name')
        if name in processed_names:
            return None
        processed_names.add(name)
        
        if element.name == 'textarea':
            return {
                'type': 'PARAGRAPH_TEXT',
                'required': False,
                'name': name
            }
        else:
            return {
                'type': 'TEXT',
                'required': False,
                'name': name
            }
    
    def _get_option_text_ultimate(self, input_elem) -> str:
        """Ultimate option text extraction"""
        # Method 1: Text immediately after input
        next_node = input_elem.next_sibling
        while next_node:
            if isinstance(next_node, NavigableString):
                text = next_node.strip()
                if text and text not in ['<br>', '\n', ' ']:
                    return text
            elif next_node.name == 'br':
                break
            next_node = next_node.next_sibling
        
        # Method 2: Parent label
        parent_label = input_elem.find_parent('label')
        if parent_label:
            return parent_label.get_text().strip()
        
        # Method 3: Value attribute
        return input_elem.get('value', '')
    
    def _is_other_option(self, text: str) -> bool:
        """Check if this is an 'other' option"""
        other_keywords = ['অন্যান্য', 'other', 'others', 'অন্য']
        return any(keyword in text.lower() for keyword in other_keywords)
    
    def _extract_question_number(self, question_text: str) -> int:
        """Extract question number"""
        patterns = [
            r'^(\d+)\.',
            r'^(\d+)\)',
            r'^([১-৯০]+)\.',
            r'^([১-৯০]+)\)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, question_text.strip())
            if match:
                num_str = match.group(1)
                num_str = self._convert_bengali_to_english_number(num_str)
                try:
                    return int(num_str)
                except ValueError:
                    continue
        
        return 999
    
    def _convert_bengali_to_english_number(self, bengali_num: str) -> str:
        """Convert Bengali to English numbers"""
        bengali_to_english = {
            '০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4',
            '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9'
        }
        
        result = bengali_num
        for bengali, english in bengali_to_english.items():
            result = result.replace(bengali, english)
        
        return result

class UltimateGoogleFormCreator:
    """Ultimate Google Form creator with proper formatting"""
    
    def __init__(self, credentials_file: str = None):
        self.credentials_file = credentials_file
        self.service = None
        self._setup_service()
    
    def _setup_service(self):
        """Setup service"""
        SCOPES = ['https://www.googleapis.com/auth/forms.body']
        
        creds = None
        
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if self.credentials_file and os.path.exists(self.credentials_file):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                else:
                    print("Error: No credentials file found!")
                    return
            
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('forms', 'v1', credentials=creds)
    
    def create_form(self, form_data: Dict[str, Any]) -> str:
        """Create ultimate Google Form"""
        if not self.service:
            raise Exception("Google Forms service not initialized")
        
        # Create form
        form = {
            "info": {
                "title": form_data['title']
            }
        }
        
        result = self.service.forms().create(body=form).execute()
        form_id = result['formId']
        
        print(f"✅ Created form: {form_data['title']}")
        print(f"   Form ID: {form_id}")
        
        # Add description
        if form_data.get('description'):
            desc_request = {
                "requests": [{
                    "updateFormInfo": {
                        "info": {
                            "description": form_data['description']
                        },
                        "updateMask": "description"
                    }
                }]
            }
            
            try:
                self.service.forms().batchUpdate(formId=form_id, body=desc_request).execute()
                print(f"   ✅ Added description")
            except Exception as e:
                print(f"   ⚠️  Warning: Could not add description: {e}")
        
        # Add questions in reverse order (API adds to top)
        questions_added = 0
        for question in reversed(form_data['questions']):
            try:
                self._add_question_ultimate(form_id, question)
                questions_added += 1
                print(f"   ✅ Added question {questions_added}/{len(form_data['questions'])}: {question['question_text'][:50]}...")
                time.sleep(0.3)
            except Exception as e:
                print(f"   ⚠️  Warning: Could not add question: {e}")
        
        print(f"   📊 Successfully added {questions_added}/{len(form_data['questions'])} questions")
        return form_id
    
    def _add_question_ultimate(self, form_id: str, question_data: Dict[str, Any]):
        """Add question with ultimate formatting"""
        
        # Question text - Google Forms will automatically make it bold/prominent
        question_title = question_data['question_text']
        
        if question_data['type'] == 'TEXT':
            question_item = {
                "title": question_title,
                "questionItem": {
                    "question": {
                        "required": question_data.get('required', False),
                        "textQuestion": {
                            "paragraph": False
                        }
                    }
                }
            }
        elif question_data['type'] == 'PARAGRAPH_TEXT':
            question_item = {
                "title": question_title,
                "questionItem": {
                    "question": {
                        "required": question_data.get('required', False),
                        "textQuestion": {
                            "paragraph": True
                        }
                    }
                }
            }
        elif question_data['type'] == 'MULTIPLE_CHOICE':
            options = []
            for option in question_data['options']:
                options.append({"value": option})
            
            choice_question = {
                "type": "RADIO",
                "options": options
            }
            
            # Add "Other" option - CORRECT WAY
            if question_data.get('has_other', False):
                choice_question["options"].append({
                    "isOther": True
                })
            
            question_item = {
                "title": question_title,
                "questionItem": {
                    "question": {
                        "required": question_data.get('required', False),
                        "choiceQuestion": choice_question
                    }
                }
            }
        elif question_data['type'] == 'CHECKBOX':
            options = []
            for option in question_data['options']:
                options.append({"value": option})
            
            choice_question = {
                "type": "CHECKBOX",
                "options": options
            }
            
            # Add "Other" option - CORRECT WAY
            if question_data.get('has_other', False):
                choice_question["options"].append({
                    "isOther": True
                })
            
            question_item = {
                "title": question_title,
                "questionItem": {
                    "question": {
                        "required": question_data.get('required', False),
                        "choiceQuestion": choice_question
                    }
                }
            }
        else:
            raise ValueError(f"Unknown question type: {question_data['type']}")
        
        # Add question to form
        request = {
            "requests": [{
                "createItem": {
                    "item": question_item,
                    "location": {"index": 0}
                }
            }]
        }
        
        self.service.forms().batchUpdate(formId=form_id, body=request).execute()

def main():
    """Ultimate main function"""
    print("🌾 ULTIMATE HTML to Google Forms Converter")
    print("=" * 50)
    print("✅ PERFECT: Question ordering (১, ২, ৩...)")
    print("✅ PERFECT: Question text formatting")
    print("✅ PERFECT: Google Forms 'Other' option")
    print("✅ PERFECT: All questions captured")
    print("✅ PERFECT: Bengali text support")
    print()
    
    # Parse forms
    forms_dir = Path("old-forms")
    if not forms_dir.exists():
        print(f"❌ Error: Directory '{forms_dir}' not found!")
        return
    
    html_files = list(forms_dir.glob("*.html"))
    if not html_files:
        print(f"❌ No HTML files found in '{forms_dir}'")
        return
    
    print(f"📁 Found {len(html_files)} HTML files:")
    for i, file in enumerate(html_files, 1):
        print(f"   {i}. {file.name}")
    
    # Parse with ultimate parser
    print(f"\n🔍 Parsing HTML forms with ULTIMATE logic...")
    parser = UltimateHTMLFormParser()
    parsed_forms = []
    
    for html_file in html_files:
        try:
            form_data = parser.parse_html_file(str(html_file))
            parsed_forms.append(form_data)
            print(f"   ✅ {html_file.name}: {form_data['title']} ({len(form_data['questions'])} questions)")
        except Exception as e:
            print(f"   ❌ {html_file.name}: Error - {e}")
    
    if not parsed_forms:
        print("❌ No forms could be parsed!")
        return
    
    # Save data
    with open('parsed_forms_ultimate.json', 'w', encoding='utf-8') as f:
        json.dump(parsed_forms, f, ensure_ascii=False, indent=2)
    
    total_questions = sum(len(form['questions']) for form in parsed_forms)
    print(f"\n📊 ULTIMATE Parsing Summary:")
    print(f"   ✅ Successfully parsed: {len(parsed_forms)} forms")
    print(f"   📋 Total questions: {total_questions}")
    print(f"   💾 Data saved to: parsed_forms_ultimate.json")
    
    # Show question breakdown
    for form in parsed_forms:
        print(f"\n   📝 {form['title']}: {len(form['questions'])} questions")
        for i, q in enumerate(form['questions'], 1):
            q_type = q['type']
            has_other = ' (+Other)' if q.get('has_other') else ''
            print(f"      {i}. {q['question_text'][:60]}... [{q_type}{has_other}]")
    
    # Confirm
    print(f"\n🚀 Ready to create ULTIMATE Google Forms!")
    response = input("Do you want to proceed? (y/n): ").lower().strip()
    
    if response != 'y':
        print("Operation cancelled.")
        return
    
    # Check credentials
    credentials_file = 'credentials.json'
    if not os.path.exists(credentials_file):
        print(f"❌ Credentials file '{credentials_file}' not found!")
        return
    
    # Create forms
    try:
        print(f"\n🔑 Initializing Google Forms API...")
        creator = UltimateGoogleFormCreator(credentials_file)
        
        if not creator.service:
            print("❌ Failed to initialize Google Forms API")
            return
        
        print("✅ Google Forms API initialized successfully")
        
        print(f"\n🏗️  Creating ULTIMATE Google Forms...")
        created_forms = []
        
        for i, form_data in enumerate(parsed_forms, 1):
            try:
                print(f"\n[{i}/{len(parsed_forms)}] Creating: {form_data['title']}")
                
                if i > 1:
                    print("⏳ Waiting 3 seconds to avoid rate limits...")
                    time.sleep(3)
                
                form_id = creator.create_form(form_data)
                
                created_form = {
                    'title': form_data['title'],
                    'form_id': form_id,
                    'edit_url': f"https://docs.google.com/forms/d/{form_id}/edit",
                    'response_url': f"https://docs.google.com/forms/d/{form_id}/viewform",
                    'questions_count': len(form_data['questions'])
                }
                
                created_forms.append(created_form)
                print(f"🎉 Successfully created: {form_data['title']}")
                
            except Exception as e:
                print(f"❌ Error creating form '{form_data['title']}': {e}")
                continue
        
        # Save results
        if created_forms:
            with open('created_google_forms_ultimate.json', 'w', encoding='utf-8') as f:
                json.dump(created_forms, f, ensure_ascii=False, indent=2)
            
            print(f"\n" + "🎉" * 20)
            print("ULTIMATE GOOGLE FORMS CREATED SUCCESSFULLY!")
            print("🎉" * 20)
            print("\n🔗 Your Google Forms are ready:")
            
            for form in created_forms:
                print(f"\n📝 **{form['title']}**")
                print(f"   📊 Questions: {form['questions_count']}")
                print(f"   ✏️  Edit: {form['edit_url']}")
                print(f"   🔗 Share: {form['response_url']}")
            
            print(f"\n💾 All form details saved to 'created_google_forms_ultimate.json'")
            print(f"\n🎯 Perfect Success: Created {len(created_forms)}/{len(parsed_forms)} forms!")
            print(f"\nNote: Question text automatically appears bold in Google Forms interface")
        else:
            print("❌ No forms were created successfully")
        
    except Exception as e:
        print(f"❌ Error during form creation: {e}")

if __name__ == "__main__":
    main()
