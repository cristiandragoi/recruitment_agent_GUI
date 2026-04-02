interface DailyPosterProps { apiUrl: string }
export default function DailyPoster({ apiUrl }: DailyPosterProps) {
  return <div className="card"><h2 className="card-title">📝 Daily Poster Agent</h2><p>Schedule and post job advertisements to Facebook groups.</p></div>
}
