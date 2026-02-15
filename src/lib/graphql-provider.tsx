/**
 * GraphQL Provider
 * Provides urql client to the application
 */

'use client';

import { Provider } from 'urql';
import { ReactNode } from 'react';
import { graphqlClient } from './graphql-client';

interface GraphQLProviderProps {
  children: ReactNode;
}

export function GraphQLProvider({ children }: GraphQLProviderProps) {
  return <Provider value={graphqlClient}>{children}</Provider>;
}
