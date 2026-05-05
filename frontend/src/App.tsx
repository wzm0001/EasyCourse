import { ConfigProvider, theme as antTheme, App } from 'antd';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider } from 'react-router-dom';
import router from '@/router';
import { useAppStore } from '@/store/app';
import { lightTheme, darkTheme } from '@/styles/theme';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export default function AppEntry() {
  const appTheme = useAppStore((s) => s.theme);

  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider
        theme={{
          ...appTheme === 'dark' ? darkTheme : lightTheme,
          algorithm:
            appTheme === 'dark'
              ? antTheme.darkAlgorithm
              : antTheme.defaultAlgorithm,
        }}
      >
        <App>
          <RouterProvider router={router} />
        </App>
      </ConfigProvider>
    </QueryClientProvider>
  );
}
