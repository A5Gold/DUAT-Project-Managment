import { useEffect } from 'react'
import { useAppStore } from '@/lib/store'

const colorMap = {
  success: 'bg-green-500',
  error: 'bg-red-500',
  info: 'bg-blue-500',
  warning: 'bg-yellow-500',
} as const

const AUTO_DISMISS_MS = 5000

function NotificationToast() {
  const notifications = useAppStore((state) => state.notifications)
  const removeNotification = useAppStore((state) => state.removeNotification)

  useEffect(() => {
    if (notifications.length === 0) {
      return
    }

    const timers = notifications.map((n) =>
      setTimeout(() => removeNotification(n.id), AUTO_DISMISS_MS)
    )

    return () => {
      timers.forEach(clearTimeout)
    }
  }, [notifications, removeNotification])

  if (notifications.length === 0) {
    return null
  }

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2">
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={`${colorMap[notification.type]} text-white px-4 py-3 rounded shadow-lg flex items-center justify-between gap-3 min-w-[280px] max-w-sm`}
        >
          <span className="text-sm">{notification.message}</span>
          <button
            type="button"
            onClick={() => removeNotification(notification.id)}
            className="shrink-0 hover:opacity-75 transition-opacity"
            aria-label="Dismiss"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      ))}
    </div>
  )
}

export default NotificationToast
