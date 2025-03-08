import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChevronDownIcon,
  ChevronRightIcon,
  CheckCircleIcon,
  ClockIcon,
  UserCircleIcon,
  ExclamationCircleIcon,
} from '@heroicons/react/24/solid';

interface Story {
  key: string;
  summary: string;
  status: string;
  assignee: string;
  priority: string;
  updated: string;
}

interface Epic {
  key: string;
  summary: string;
  status: string;
  assignee: string;
  progress: {
    total: number;
    completed: number;
  };
  stories: Story[];
}

interface ProjectSummaryData {
  projectName: string;
  projectKey: string;
  lastUpdated: string;
  epics: Epic[];
}

interface ProjectSummaryProps {
  data: ProjectSummaryData;
}

export const ProjectSummary: React.FC<ProjectSummaryProps> = ({ data }) => {
  const [expandedEpics, setExpandedEpics] = React.useState<string[]>([]);

  const toggleEpic = (epicKey: string) => {
    setExpandedEpics(prev =>
      prev.includes(epicKey)
        ? prev.filter(key => key !== epicKey)
        : [...prev, epicKey]
    );
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'done':
        return 'bg-green-500';
      case 'in progress':
        return 'bg-blue-500';
      case 'blocked':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="bg-gray-900 text-gray-100 rounded-lg p-6 shadow-xl">
      {/* Project Header */}
      <div className="border-b border-gray-700 pb-4 mb-6">
        <h2 className="text-2xl font-bold text-blue-400 mb-2">
          {data.projectName} ({data.projectKey})
        </h2>
        <div className="flex items-center text-sm text-gray-400">
          <ClockIcon className="h-4 w-4 mr-2" />
          Last Updated: {formatDate(data.lastUpdated)}
        </div>
      </div>

      {/* Epics List */}
      <div className="space-y-4">
        {data.epics.map(epic => (
          <div
            key={epic.key}
            className="bg-gray-800 rounded-lg overflow-hidden"
          >
            {/* Epic Header */}
            <motion.button
              onClick={() => toggleEpic(epic.key)}
              className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-700 transition-colors"
            >
              <div className="flex items-center space-x-3">
                {expandedEpics.includes(epic.key) ? (
                  <ChevronDownIcon className="h-5 w-5 text-blue-400" />
                ) : (
                  <ChevronRightIcon className="h-5 w-5 text-blue-400" />
                )}
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-medium">{epic.summary}</span>
                    <span className="text-sm text-gray-400">{epic.key}</span>
                  </div>
                  <div className="flex items-center space-x-3 text-sm text-gray-400">
                    <span className="flex items-center">
                      <UserCircleIcon className="h-4 w-4 mr-1" />
                      {epic.assignee}
                    </span>
                    <span className={`px-2 py-0.5 rounded-full text-xs ${getStatusColor(epic.status)}`}>
                      {epic.status}
                    </span>
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-400">
                  Progress: {epic.progress.completed}/{epic.progress.total}
                </div>
                <div className="w-32 h-2 bg-gray-700 rounded-full mt-1">
                  <div
                    className="h-full bg-blue-500 rounded-full"
                    style={{
                      width: `${(epic.progress.completed / epic.progress.total) * 100}%`,
                    }}
                  />
                </div>
              </div>
            </motion.button>

            {/* Stories List */}
            <AnimatePresence>
              {expandedEpics.includes(epic.key) && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="border-t border-gray-700"
                >
                  <div className="p-4 space-y-3">
                    {epic.stories.map(story => (
                      <div
                        key={story.key}
                        className="bg-gray-700 rounded-lg p-3 hover:bg-gray-600 transition-colors"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <div>
                              <div className="flex items-center space-x-2">
                                <span>{story.summary}</span>
                                <span className="text-sm text-gray-400">
                                  {story.key}
                                </span>
                              </div>
                              <div className="flex items-center space-x-3 text-sm text-gray-400 mt-1">
                                <span className="flex items-center">
                                  <UserCircleIcon className="h-4 w-4 mr-1" />
                                  {story.assignee}
                                </span>
                                <span className={`px-2 py-0.5 rounded-full text-xs ${getStatusColor(story.status)}`}>
                                  {story.status}
                                </span>
                                {story.priority && (
                                  <span className="flex items-center">
                                    <ExclamationCircleIcon className="h-4 w-4 mr-1" />
                                    {story.priority}
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                          <div className="text-sm text-gray-400">
                            {formatDate(story.updated)}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        ))}
      </div>
    </div>
  );
};
