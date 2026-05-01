import React, { useEffect, useState } from 'react'
import { getIncentives } from '../api'

const STATUS_STYLE = {
  PAID:    'bg-green-100 text-green-700',
  PENDING: 'bg-yellow-100 text-yellow-700',
  PROCESSING: 'bg-blue-100 text-blue-700',
}

export default function IncentiveLedger() {
  const [items, setItems] = useState([])
  const [total, setTotal] = useState(0)

  useEffect(() => {
    getIncentives(1).then(r => { setItems(r.data.incentives); setTotal(r.data.total_pending) })
  }, [])

  return (
    <div className="bg-white rounded-2xl shadow p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-gray-700">Incentive Ledger</h2>
        <span className="text-green-700 font-bold">₹{total} pending</span>
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-gray-500 border-b">
            <th className="pb-2">Patient</th>
            <th className="pb-2">Date</th>
            <th className="pb-2">Amount</th>
            <th className="pb-2">Status</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item, i) => (
            <tr key={i} className="border-b last:border-0 hover:bg-gray-50">
              <td className="py-3">{item.patient_name}</td>
              <td className="py-3 text-gray-400">{item.visit_date}</td>
              <td className="py-3 font-semibold">₹{item.amount}</td>
              <td className="py-3">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${STATUS_STYLE[item.status] || ''}`}>
                  {item.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}