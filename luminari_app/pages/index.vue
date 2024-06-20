<script setup lang="ts">
import { useChat } from 'ai/vue';

const { messages, input, handleSubmit, data } = useChat();
// const ogs = require('open-graph-scraper');
// const options = { url: 'https://sdk.vercel.ai/docs/getting-started/nuxt' };
// ogs(options)
//   .then((data) => {
//     const { error, response } = data;
//     console.log('error:', error);  // This returns true or false. True if there was an error. The error itself is inside the result object.
//     console.log('response:', response); // This contains response from the Fetch API
//   });

</script>

<template>
  <div class="flex flex-col w-full max-w-md py-24 mx-auto stretch">
    <div v-for="m in messages" key="m.id" class="whitespace-pre-wrap">
      {{ m.role === 'user' ? 'User: ' : 'AI: ' }}
      {{ m.content }}
      <div v-if="m.role!='user'">
        <pre>{{JSON.stringify(data, null, 2)}}</pre>
      </div>
    </div>

    <form @submit="handleSubmit">
      <input class="fixed bottom-0 w-full max-w-md p-2 mb-8 border border-gray-300 rounded shadow-xl" v-model="input"
        placeholder="Say something..." />
    </form>
  </div>
</template>
