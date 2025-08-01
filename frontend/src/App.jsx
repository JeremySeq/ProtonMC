import Dashboard from './dashboard/Dashboard.jsx'
import Overview from './dashboard/Overview.jsx'
import Console from './dashboard/Console.jsx'
import Backups from './dashboard/Backups.jsx'
import Mods from './dashboard/Mods.jsx'
import ServerMenu from './ServerMenu'
import {
  createBrowserRouter,
  RouterProvider,
  redirect
} from "react-router-dom";
import LoginPage from './LoginPage';
import {hasAuth} from './AuthorizationHelper';
import ErrorPage from './ErrorPage'
import { NotificationProvider } from './NotificationContext';
import ServerCreator from "./ServerCreator.jsx";
import AppLayout from "./AppLayout.jsx";

function App() {
  const router = createBrowserRouter([
    {
      element: <AppLayout />,  // Wrap all routes here
      children: [
        {
          path: "/",
          loader() {
            if (hasAuth()) {
              return redirect("/servers");
            } else {
              return redirect("/login");
            }
          },
          errorElement: <ErrorPage />
        },
        {
          path: "/login",
          element: <LoginPage />
        },
        {
          path: "/servers",
          element: <ServerMenu />,
          loader: protectedLoader
        },
        {
          path: "/create",
          element: <ServerCreator />,
          loader: protectedLoader
        },
        {
          path: "/servers/:serverName",
          element: <Dashboard />,
          loader: protectedLoader,
          children: [
            { path: "overview", element: <Overview /> },
            { path: "console", element: <Console /> },
            { path: "backups", element: <Backups /> },
            { path: "mods", element: <Mods /> }
          ]
        }
      ]
    }
  ]);

  return (
    <>
      <NotificationProvider>
        <RouterProvider router={router} />
      </NotificationProvider>
    </>
  )
}


export default App

function protectedLoader() {
  if (hasAuth()) {
    return null;
  } else {
    return redirect("/login");
  }
}