import React, { useState, Component, ErrorInfo, ReactNode } from 'react';
import { Sparkles, Target, Users, RefreshCw } from 'lucide-react';

// Error Boundary Component
class ErrorBoundary extends Component<{ children: ReactNode }, { hasError: boolean; error: Error | null }> {
  constructor(props: { children: ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <h2 className="text-lg font-semibold text-red-700">Something went wrong</h2>
          <p className="text-red-600">{this.state.error?.message || 'Unknown error occurred'}</p>
          <button 
            onClick={() => this.setState({ hasError: false, error: null })}
            className="mt-2 px-4 py-2 bg-red-100 text-red-700 rounded hover:bg-red-200"
          >
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

interface TargetAudience {
  age: string;
  location: string;
  lifestyle: string;
}

interface CampaignForm {
  industry: string;
  target_audience: TargetAudience;
  genders: string[];
  budget_range: string;
  campaign_objective: string;
  constraints: string;
  additional_comments: string;
}

interface KPIMetrics {
  [key: string]: string | number | string[] | { [key: string]: string | number };
}

interface CampaignResult {
  big_idea: string;
  key_messages: string[];
  channels: string[];
  kpis: KPIMetrics;
}

function App() {
  const [formData, setFormData] = useState<CampaignForm>({
    industry: '',
    target_audience: {
      age: '',
      location: '',
      lifestyle: ''
    },
    genders: [],
    budget_range: '',
    campaign_objective: '',
    constraints: '',
    additional_comments: ''
  });

  const [result, setResult] = useState<CampaignResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [, setError] = useState<string | null>(null);
  const [comment, setComment] = useState('');
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [showCommentDialog, setShowCommentDialog] = useState(false);

  const handleInputChange = (field: string, value: string) => {
    if (field.startsWith('target_audience.')) {
      const audienceField = field.split('.')[1];
      setFormData(prev => ({
        ...prev,
        target_audience: {
          ...prev.target_audience,
          [audienceField]: value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [field]: value
      }));
    }
  };

  const handleGenderChange = (gender: string) => {
    setFormData(prev => ({
      ...prev,
      genders: prev.genders.includes(gender)
        ? prev.genders.filter(g => g !== gender)
        : [...prev.genders, gender]
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      console.log('Sending request with data:', formData);
      const response = await fetch('http://localhost:8000/generate-campaign', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
        }),
      });

      console.log('Response status:', response.status);
      const responseText = await response.text();
      console.log('Raw response:', responseText);
      
      let data;
      try {
        data = responseText ? JSON.parse(responseText) : {};
      } catch (e) {
        console.error('Failed to parse JSON response:', e);
        throw new Error('Invalid JSON response from server');
      }

      if (!response.ok) {
        console.error('API Error:', data);
        throw new Error(data.detail || `HTTP error! status: ${response.status}`);
      }

      console.log('Parsed response data:', data);
      
      if (data.status === 'success' && data.data) {
        let resultData;
        try {
          resultData = typeof data.data === 'string' ? JSON.parse(data.data) : data.data;
          console.log('Processed result data:', resultData);
          // Ensure all expected properties exist with default values
          setResult({
            big_idea: resultData.big_idea || '',
            key_messages: Array.isArray(resultData.key_messages) ? resultData.key_messages : [],
            channels: Array.isArray(resultData.channels) ? resultData.channels : [],
            kpis: resultData.kpis || {}
          });
        } catch (e) {
          console.error('Error parsing result data:', e);
          throw new Error('Failed to process campaign data');
        }
      } else {
        console.error('Unexpected response format:', data);
        throw new Error('Invalid response format from server');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred';
      setError(`Failed to generate campaign: ${errorMessage}`);
      console.error('API Error:', err);
      
      // Fallback to mock data for demonstration
      setResult({
        big_idea: "Fit & Fast Bangkok: Your Health on a Plate, Delivered to Your Doorstep",
        key_messages: [
          "Eat well without the wait – healthy meals that fit your busy life.",
          "Fuel your fitness goals with chef-crafted, organic ingredients.",
          "Skip the gym and enjoy convenience that doesn't compromise quality.",
          "Join thousands of working professionals who are eating better, moving more, and living their best life."
        ],
        channels: [
          "Facebook (30% of budget allocated for targeted ads and community engagement)",
          "TikTok (25% allocated for creative, short-form video content)",
          "Google (20% for search-based visibility and lead capture)",
          "Offline Events (25% for face-to-face interaction and trust-building)"
        ],
        kpis: {
          reach: "120,000 - 150,000 (70% of budget allocated to Facebook and TikTok for social reach)",
          leads: "3,000 - 4,500 (via challenge participation, influencer content, and event lead capture)",
          cost_per_lead: "111 - 167 THB (based on conversion rates from interactive engagement activities)",
          roas: "3.6 - 5.0x (assuming average order value of 1,000 THB and 20-30% conversion rate from leads)",
          ctr: "2.5% - 3.5% (optimizing for high-performing platforms like TikTok and Google)",
          conversion_rate: "20% - 25% (from lead generation to first purchase based on engagement activities)"
        }
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCommentSubmit = async () => {
    if (!comment.trim() || !result) return;
    
    setIsRegenerating(true);
    setShowCommentDialog(false);
    
    try {
      const response = await fetch('http://localhost:8000/regenerate-campaign', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          old_campaign: result,
          client_comment: comment,
          modifications: {
            feedback: comment
          }
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to regenerate campaign');
      }

      const data = await response.json();
      console.log('Regeneration response:', data);
      
      if (data.status === 'success' && data.data) {
        // Parse the response data to ensure it matches the expected format
        const responseData = typeof data.data === 'string' ? JSON.parse(data.data) : data.data;
        setResult({
          big_idea: responseData.big_idea || '',
          key_messages: Array.isArray(responseData.key_messages) ? responseData.key_messages : [],
          channels: Array.isArray(responseData.channels) ? responseData.channels : [],
          kpis: responseData.kpis || {}
        });
        setComment('');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to regenerate campaign';
      setError(`Failed to regenerate campaign: ${errorMessage}`);
      console.error('Regeneration error:', err);
    } finally {
      setIsRegenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-100 py-12 px-4">
      {/* Comment Dialog */}
      {showCommentDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Add Your Feedback</h3>
            <p className="text-sm text-gray-600 mb-3">
              What would you like to change about the current campaign?
            </p>
            <textarea
              className="w-full p-3 border rounded-lg mb-4 h-32"
              placeholder="Enter your feedback here..."
              value={comment}
              onChange={(e) => setComment(e.target.value)}
            />
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowCommentDialog(false);
                  setComment('');
                }}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                disabled={isRegenerating}
              >
                Cancel
              </button>
              <button
                onClick={handleCommentSubmit}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center"
                disabled={!comment.trim() || isRegenerating}
              >
                {isRegenerating ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Regenerating...
                  </>
                ) : (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Regenerate
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-purple-600 to-blue-600 rounded-full mb-6">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Campaign Generator
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Generate data-driven marketing campaigns tailored to your business objectives
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Form Section */}
          <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100 overflow-y-auto max-h-[calc(100vh-200px)] flex flex-col">
            <h2 className="text-2xl font-semibold text-gray-900 mb-6 flex items-center">
              <Target className="w-6 h-6 mr-3 text-purple-600" />
              Campaign Details
            </h2>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Industry */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Industry
                </label>
                <input
                  type="text"
                  value={formData.industry}
                  onChange={(e) => handleInputChange('industry', e.target.value)}
                  placeholder="e.g., Healthy Food Delivery"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200"
                  required
                />
              </div>

              {/* Target Audience */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-gray-800 flex items-center">
                  <Users className="w-5 h-5 mr-2 text-blue-600" />
                  Target Audience
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Age Range
                    </label>
                    <input
                      type="text"
                      value={formData.target_audience.age}
                      onChange={(e) => handleInputChange('target_audience.age', e.target.value)}
                      placeholder="e.g., 25-35"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Location
                    </label>
                    <input
                      type="text"
                      value={formData.target_audience.location}
                      onChange={(e) => handleInputChange('target_audience.location', e.target.value)}
                      placeholder="e.g., Bangkok, Thailand"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Lifestyle/Interests
                  </label>
                  <input
                    type="text"
                    value={formData.target_audience.lifestyle}
                    onChange={(e) => handleInputChange('target_audience.lifestyle', e.target.value)}
                    placeholder="e.g., Health-conscious, Busy professionals"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    required
                  />
                </div>
              </div>

              {/* Genders */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Target Genders
                </label>
                <div className="flex flex-wrap gap-3">
                  {['Male', 'Female', 'Non-binary', 'All'].map((gender) => (
                    <button
                      key={gender}
                      type="button"
                      onClick={() => handleGenderChange(gender)}
                      className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                        formData.genders.includes(gender)
                          ? 'bg-blue-100 text-blue-700 border border-blue-200'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200 border border-gray-200'
                      }`}
                    >
                      {gender}
                    </button>
                  ))}
                </div>
              </div>

              {/* Campaign Objective */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Campaign Objective
                </label>
                <select
                  value={formData.campaign_objective}
                  onChange={(e) => handleInputChange('campaign_objective', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  required
                >
                  <option value="">Select objective</option>
                  <option value="Brand Awareness">Brand Awareness</option>
                  <option value="Consideration / Engagement">Consideration / Engagement</option>
                  <option value="Lead Generation / Acquisition">Lead Generation / Acquisition</option>
                  <option value="Sales / Conversion">Sales / Conversion</option>
                  <option value="Retention / Loyalty">Retention / Loyalty</option>
                  <option value="Advocacy / Referral">Advocacy / Referral</option>
                </select>
              </div>

              {/* Budget Range */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Budget Range (THB)
                </label>
                <input
                  type="text"
                  value={formData.budget_range}
                  onChange={(e) => handleInputChange('budget_range', e.target.value)}
                  placeholder="e.g., 500,000 THB"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  required
                />
              </div>

              {/* Constraints */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Any Constraints?
                </label>
                <textarea
                  value={formData.constraints}
                  onChange={(e) => handleInputChange('constraints', e.target.value)}
                  placeholder="e.g., Must include specific hashtags, avoid certain topics, etc."
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent min-h-[100px]"
                />
              </div>

              {/* Additional Comments */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Additional Comments
                </label>
                <textarea
                  value={formData.additional_comments}
                  onChange={(e) => handleInputChange('additional_comments', e.target.value)}
                  placeholder="Any other details or preferences..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent min-h-[100px]"
                />
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white font-medium py-3 px-6 rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center justify-center"
              >
                {isLoading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Generating...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5 mr-2" />
                    Generate Campaign
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Results Section */}
          <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100 overflow-y-auto max-h-[calc(100vh-200px)] flex flex-col">
            <div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-6 flex items-center">
                <Sparkles className="w-6 h-6 mr-3 text-purple-600" />
                Campaign Results
              </h2>

            {isLoading ? (
              <div className="flex flex-col items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mb-4"></div>
                <p className="text-gray-600">Generating your campaign...</p>
              </div>
            ) : result ? (
              <div className="space-y-8">
                {/* Big Idea */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-3">💡 Big Idea</h3>
                  <div className="bg-purple-50 rounded-xl p-6 border-l-4 border-purple-500">
                    <p className="text-gray-800 text-lg">{result.big_idea || 'No big idea generated yet'}</p>
                  </div>
                </div>

                {/* Key Messages */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">🎯 Key Messages</h3>
                  <div className="space-y-3">
                    {(result.key_messages || []).map((message, index) => (
                      <div key={index} className="bg-gray-50 rounded-lg p-4 border-l-4 border-blue-500">
                        <p className="text-gray-700">{message}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Channels */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">📢 Marketing Channels</h3>
                  <div className="grid gap-3">
                    {(result.channels || []).map((channel, index) => (
                      <div key={index} className="bg-green-50 rounded-lg p-4 border border-green-200">
                        <p className="text-gray-700">{channel}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* KPIs */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">📊 Key Performance Indicators</h3>
                  <div className="grid gap-4">
                    {Object.entries(result.kpis).map(([key, value]) => {
                      if (typeof value === 'object' && value !== null) {
                        return (
                          <div key={key} className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
                            <h4 className="font-medium text-gray-800 capitalize mb-2">
                              {key.replace(/_/g, ' ')}
                            </h4>
                            {Array.isArray(value) ? (
                              <ul className="list-disc pl-5 space-y-1">
                                {(value as string[]).map((item, i) => (
                                  <li key={i} className="text-gray-700">{item}</li>
                                ))}
                              </ul>
                            ) : (
                              <div className="space-y-2">
                                {Object.entries(value).map(([subKey, subValue]) => (
                                  <div key={subKey}>
                                    <span className="font-medium">{subKey.replace(/_/g, ' ')}: </span>
                                    <span className="text-gray-700">
                                      {typeof subValue === 'string' || typeof subValue === 'number'
                                        ? subValue
                                        : JSON.stringify(subValue)}
                                    </span>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        );
                      }

                      return (
                        <div key={key} className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
                          <h4 className="font-medium text-gray-800 capitalize mb-2">
                            {key.replace(/_/g, ' ')}
                          </h4>
                          <p className="text-gray-700">
                            {typeof value === 'string' || typeof value === 'number'
                              ? value
                              : JSON.stringify(value)}
                          </p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-12">
                <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500 text-lg">
                  Fill in the campaign details to generate your marketing strategy
                </p>
              </div>
            )}
            </div> {/* End of results content */}
            
            {/* Regenerate Button at Bottom */}
            {result && (
              <div className="mt-8 pt-6 border-t border-gray-100">
                <button
                  type="button"
                  onClick={() => setShowCommentDialog(true)}
                  disabled={isRegenerating}
                  className={`w-full py-3 px-6 rounded-lg font-medium flex items-center justify-center ${
                    isRegenerating
                      ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                      : 'bg-white text-blue-600 border-2 border-blue-200 hover:bg-blue-50 transition-colors'
                  }`}
                >
                  {isRegenerating ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Regenerating...
                    </>
                  ) : (
                    <>
                      <RefreshCw className="w-5 h-5 mr-2" />
                      Regenerate with Feedback
                    </>
                  )}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// Wrap the App component with ErrorBoundary
const AppWithErrorBoundary = () => (
  <ErrorBoundary>
    <App />
  </ErrorBoundary>
);

export default AppWithErrorBoundary;