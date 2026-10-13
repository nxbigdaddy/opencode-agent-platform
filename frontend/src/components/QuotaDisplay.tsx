import { useState, useEffect } from 'react'
import './QuotaDisplay.css'

interface QuotaInfo {
  has_quota: boolean
  quota: number
  used_quota: number
  remaining: number
  message: string
}

function QuotaDisplay() {
  const [quota, setQuota] = useState<QuotaInfo | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadQuota()
    // 每 30 秒刷新一次配额
    const interval = setInterval(loadQuota, 30000)
    return () => clearInterval(interval)
  }, [])

  const loadQuota = async () => {
    try {
      const response = await fetch('/api/v1/quota', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('auth-storage') ? JSON.parse(localStorage.getItem('auth-storage')!).accessToken : ''}`,
        },
      })
      if (response.ok) {
        const data = await response.json()
        setQuota(data)
      }
    } catch (error) {
      console.error('加载配额失败:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading || !quota) {
    return null
  }

  const usagePercent = quota.quota > 0 ? (quota.used_quota / quota.quota) * 100 : 0
  const isLow = usagePercent > 80
  const isCritical = usagePercent > 95

  return (
    <div className={`quota-display ${isCritical ? 'critical' : isLow ? 'low' : ''}`}>
      <div className="quota-info">
        <span className="quota-label">Token 配额</span>
        <div className="quota-bar-container">
          <div 
            className="quota-bar" 
            style={{ 
              width: `${usagePercent}%`,
              backgroundColor: isCritical ? '#dc2626' : isLow ? '#f59e0b' : '#3b82f6'
            }}
          />
        </div>
        <span className="quota-text">
          {quota.remaining.toLocaleString()} / {quota.quota.toLocaleString()}
        </span>
      </div>
      {!quota.has_quota && (
        <div className="quota-warning">
          ⚠️ 配额已用完，请联系管理员
        </div>
      )}
    </div>
  )
}

export default QuotaDisplay
