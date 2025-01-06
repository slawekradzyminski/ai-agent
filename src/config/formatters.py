import logging
from datetime import datetime

class OpenAIFormatter(logging.Formatter):
    def _format_message(self, msg):
        if isinstance(msg, dict):
            msg_type = msg.get('type', 'unknown')
            content = msg.get('content', '')
            if msg_type.lower() == 'system':
                return f"System:\n{content}"
            elif msg_type.lower() == 'human':
                return f"Human: {content}"
            else:
                return f"{msg_type}: {content}"
        return str(msg)
    
    def format(self, record):
        if hasattr(record, 'openai_request'):
            data = record.openai_request
            formatted_messages = []
            for msg in data.get('messages', []):
                formatted_msg = self._format_message(msg)
                formatted_msg = formatted_msg.replace('\n', '\n  ')
                formatted_messages.append(formatted_msg)
                    
            record.msg = "\n" + "="*80 + "\n" + \
                        f"OpenAI Request - ID: {data.get('id', 'N/A')}\n" + \
                        f"Model: {data.get('model', 'N/A')}\n" + \
                        f"Temperature: {data.get('temperature', 0.0)}\n" + \
                        f"Messages:\n  {'\n  '.join(formatted_messages)}"
            if data.get('timestamp'):
                record.msg += f"\nTimestamp: {data['timestamp']}"
            if data.get('note'):
                record.msg += f"\nNote: {data['note']}"
            record.msg += "\n" + "="*80
                
        elif hasattr(record, 'openai_response'):
            data = record.openai_response
            record.msg = "\n" + "-"*80 + "\n" + \
                        f"OpenAI Response - ID: {data.get('id', 'N/A')}\n" + \
                        f"Content: {data.get('content', '')}"
            
            if any(data.get(k, 0) > 0 for k in ['total_tokens', 'completion_tokens', 'prompt_tokens']):
                record.msg += f"\nTokens Used:" + \
                            f"\n  Total: {data.get('total_tokens', 0):,d}" + \
                            f"\n  Completion: {data.get('completion_tokens', 0):,d}" + \
                            f"\n  Prompt: {data.get('prompt_tokens', 0):,d}"
            
            if data.get('finish_reason'):
                record.msg += f"\nFinish Reason: {data['finish_reason']}"
            if data.get('timestamp'):
                record.msg += f"\nTimestamp: {data['timestamp']}"
            if data.get('note'):
                record.msg += f"\nNote: {data['note']}"
            record.msg += "\n" + "-"*80
                
        elif hasattr(record, 'openai_error'):
            data = record.openai_error
            record.msg = "\n" + "!"*80 + "\n" + \
                        f"OpenAI Error - ID: {data.get('id', 'N/A')}\n" + \
                        f"Error Type: {data.get('error_type', 'N/A')}\n" + \
                        f"Error Message: {data.get('error_message', 'N/A')}\n" + \
                        f"Timestamp: {data.get('timestamp', datetime.now().isoformat())}"
            if data.get('note'):
                record.msg += f"\nNote: {data['note']}"
            record.msg += "\n" + "!"*80
                
        return super().format(record) 