import React, { useEffect, useState } from 'react';
import SidebarLayout from '../components/SidebarLayout';
import api from '../services/api';
import { ShieldCheck, Plus, Trash2, Layers, CheckCircle2, User } from 'lucide-react';

const AdminDashboardPage = () => {
  const [taxonomy, setTaxonomy] = useState(null);
  const [users, setUsers] = useState([]);
  const [newSkillName, setNewSkillName] = useState('');
  const [newSkillCategory, setNewSkillCategory] = useState('programming_languages');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAdminData();
  }, []);

  const fetchAdminData = () => {
    setLoading(true);
    Promise.all([
      api.get('/admin/taxonomy'),
      api.get('/admin/users')
    ]).then(([taxRes, userRes]) => {
      setTaxonomy(taxRes.data);
      setUsers(userRes.data || []);
      setLoading(false);
    }).catch(err => {
      console.error(err);
      setLoading(false);
    });
  };

  const handleAddSkill = (e) => {
    e.preventDefault();
    if (!newSkillName.trim()) return;

    api.post('/admin/skills', {
      name: newSkillName.trim(),
      category: newSkillCategory,
      priority_level: 'Medium'
    }).then(() => {
      setNewSkillName('');
      fetchAdminData();
    }).catch(err => console.error(err));
  };

  const handleDeleteSkill = (skillId) => {
    api.delete(`/admin/skills/${skillId}`)
      .then(() => fetchAdminData())
      .catch(err => console.error(err));
  };

  return (
    <SidebarLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="glass-card rounded-3xl p-8 border border-slate-800/80 shadow-2xl space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-semibold uppercase tracking-wider">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Platform Administration & Taxonomy Management</span>
          </div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">Admin Console</h1>
          <p className="text-xs text-slate-400">
            Manage canonical skill taxonomy dictionaries and view registered users across the platform.
          </p>
        </div>

        {/* Add Skill to Taxonomy Form */}
        <div className="glass-card rounded-3xl p-6 border border-slate-800/80 shadow-2xl space-y-4">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Plus className="w-4 h-4 text-amber-400" />
            <span>Add New Canonical Skill to Taxonomy</span>
          </h3>

          <form onSubmit={handleAddSkill} className="flex flex-col sm:flex-row gap-3">
            <input
              type="text"
              required
              value={newSkillName}
              onChange={(e) => setNewSkillName(e.target.value)}
              placeholder="Skill Name (e.g., Kubernetes, Rust, GraphQL)"
              className="flex-1 p-3 rounded-2xl bg-slate-900 border border-slate-700/80 text-xs font-semibold text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
            />
            <select
              value={newSkillCategory}
              onChange={(e) => setNewSkillCategory(e.target.value)}
              className="p-3 rounded-2xl bg-slate-900 border border-slate-700/80 text-xs font-semibold text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
            >
              <option value="programming_languages">Programming Languages</option>
              <option value="frontend">Frontend</option>
              <option value="backend">Backend</option>
              <option value="database">Database</option>
              <option value="cloud_devops">Cloud & DevOps</option>
              <option value="data_ai">Data & AI</option>
            </select>
            <button
              type="submit"
              className="px-6 py-3 rounded-2xl text-xs font-extrabold text-white gradient-bg shadow-glow hover:opacity-95"
            >
              Add Skill
            </button>
          </form>
        </div>

        {/* User Management List */}
        <div className="glass-card rounded-3xl p-6 border border-slate-800/80 shadow-2xl space-y-4">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <User className="w-4 h-4 text-indigo-400" />
            <span>Registered Users ({users.length})</span>
          </h3>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs font-semibold">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider">
                  <th className="py-3 px-4">ID</th>
                  <th className="py-3 px-4">Full Name</th>
                  <th className="py-3 px-4">Email</th>
                  <th className="py-3 px-4">Role</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {users.map(u => (
                  <tr key={u.id} className="hover:bg-slate-800/40">
                    <td className="py-3 px-4 text-slate-400">#{u.id}</td>
                    <td className="py-3 px-4 text-white font-bold">{u.full_name}</td>
                    <td className="py-3 px-4 text-slate-300">{u.email}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${u.is_admin ? 'bg-amber-500/20 text-amber-400' : 'bg-slate-800 text-slate-400'}`}>
                        {u.is_admin ? 'ADMIN' : 'USER'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </SidebarLayout>
  );
};

export default AdminDashboardPage;
