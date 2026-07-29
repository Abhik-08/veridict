
export function SkeletonRow() {
  return (
    <tr className="animate-pulse border-b border-slate-800/60">
      <td className="py-3.5 px-4"><div className="h-4 bg-slate-800 rounded w-3/4"></div></td>
      <td className="py-3.5 px-4"><div className="h-5 bg-slate-800 rounded-full w-20"></div></td>
      <td className="py-3.5 px-4"><div className="h-4 bg-slate-800 rounded w-12"></div></td>
      <td className="py-3.5 px-4"><div className="h-4 bg-slate-800 rounded w-12"></div></td>
      <td className="py-3.5 px-4"><div className="h-5 bg-slate-800 rounded-full w-16"></div></td>
      <td className="py-3.5 px-4"><div className="h-4 bg-slate-800 rounded w-24"></div></td>
      <td className="py-3.5 px-4"><div className="h-6 bg-slate-800 rounded w-16"></div></td>
    </tr>
  )
}

export function SkeletonCard() {
  return (
    <div className="animate-pulse p-5 rounded-xl bg-slate-900/80 border border-slate-800/80 space-y-3">
      <div className="flex items-center justify-between">
        <div className="h-3 bg-slate-800 rounded w-24"></div>
        <div className="w-7 h-7 bg-slate-800 rounded-lg"></div>
      </div>
      <div className="h-7 bg-slate-800 rounded w-16"></div>
      <div className="h-2.5 bg-slate-800 rounded w-32"></div>
    </div>
  )
}

export function SkeletonDetailModal() {
  return (
    <div className="animate-pulse space-y-6">
      <div className="h-6 bg-slate-800 rounded w-1/2"></div>
      <div className="grid grid-cols-3 gap-4">
        <div className="h-16 bg-slate-800 rounded-lg"></div>
        <div className="h-16 bg-slate-800 rounded-lg"></div>
        <div className="h-16 bg-slate-800 rounded-lg"></div>
      </div>
      <div className="space-y-2">
        <div className="h-4 bg-slate-800 rounded w-1/4"></div>
        <div className="h-20 bg-slate-800 rounded-lg"></div>
      </div>
      <div className="space-y-2">
        <div className="h-4 bg-slate-800 rounded w-1/4"></div>
        <div className="h-24 bg-slate-800 rounded-lg"></div>
      </div>
    </div>
  )
}
