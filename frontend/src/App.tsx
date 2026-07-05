import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { RootLayout } from '@/layouts'
import { HomePage } from '@/pages'

const router = createBrowserRouter([
  {
    element: <RootLayout />,
    children: [
      {
        path: '/',
        element: <HomePage />,
      },
    ],
  },
])

export default function App() {
  return <RouterProvider router={router} />
}
