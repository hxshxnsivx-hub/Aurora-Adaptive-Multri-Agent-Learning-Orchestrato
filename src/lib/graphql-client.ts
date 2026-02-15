/**
 * GraphQL Client Configuration
 * urql client for GraphQL queries and mutations
 */

import { createClient, cacheExchange, fetchExchange, Client } from 'urql';

const GRAPHQL_URL = process.env.NEXT_PUBLIC_GRAPHQL_URL || 'http://localhost:8000/graphql';

// Create urql client
export const graphqlClient: Client = createClient({
  url: GRAPHQL_URL,
  exchanges: [cacheExchange, fetchExchange],
  fetchOptions: () => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
    
    return {
      headers: {
        authorization: token ? `Bearer ${token}` : '',
      },
    };
  },
});

export default graphqlClient;
