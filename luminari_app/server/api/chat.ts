import { createOllama } from 'ollama-ai-provider';
import { generateText, tool, StreamingTextResponse, streamText, StreamData } from 'ai';
import { z } from 'zod';
import { createOpenAI } from '@ai-sdk/openai';
const template=''
function callTools() {
    
}

export default defineLazyEventHandler(async () => {

    const openai = createOpenAI({
        
        baseURL:'http://127.0.0.1:4200/v1',
        apiKey:'sk-xxx',

    });
   
    return defineEventHandler(async (event: any) => {
        const { messages } = await readBody(event);
        console.log('Hi')
        console.log(messages);

        const response = await $fetch('http://127.0.0.1:4201/tool_response/', {
            method: 'POST', // or 'POST'
            headers: {
                'Content-Type': 'application/json',
                // 'Authorization': 'Bearer ' + token // if you need to include a token
            },
            body: JSON.stringify({
                query: messages[messages.length - 1].content,

            }) // body data type must match "Content-Type" header
        }).catch((error) => {
            console.error('Error:', error);
        });
        console.log(response);
        // let data = JSON.parse(response);       
        // let urls = data.map(data => data.url);
        let msg=response[0]
        let urls=response[1]
        console.log('Messages:::')
        console.log(msg);
        const result = await streamText({
            model: openai('hermes'),
            messages: msg,            
        });
        const url_data = new StreamData();

        url_data.append({ urls: urls });

        const stream = result.toAIStream({
            onFinal(_) {
                url_data.close();
            },
        });
        return new StreamingTextResponse(stream, {}, url_data);
    });
});