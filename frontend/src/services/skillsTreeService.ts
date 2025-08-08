import axios from 'axios';
import { getAuthHeader, endpoint } from '../utils/api';

// Define TreeNode interface for the skills tree
export interface SkillsTreeNode {
  id: string;
  label: string;
  type: "root" | "skill" | "outcome" | "career";
  level: number;
  actions?: string[];
  children?: SkillsTreeNode[];
}

interface SkillsTreeResponse {
  tree: SkillsTreeNode;
}
const SKILLS_TREE_PROMPT = `
You are TREE-ENGINE-SKILLS, an advanced assistant trained to generate deeply structured, technical, and realistic Skills Development Trees.

Your task is to generate a **multi-path, multi-depth technical skills graph** that shows how a learner can progress from beginner concepts to specialized, in-demand capabilities.

---

# INPUT

Start from this learner profile:
"{user_profile_input}"

---

# OBJECTIVE

Design a **nonlinear**, richly interconnected learning journey.  
The output should:
- Map out foundational skills ➝ intermediate techniques ➝ advanced specialization
- Allow **skills to converge** to unlock new abilities or career
- Include **actual books, thinkers, frameworks, tools, math, theory, and stacks**

This is not a school curriculum. This is how the **real world** learns.

---

# STRUCTURE

- Use nested nodes.
- Every node is either:
  - "root" (the learner’s starting point)
  - "skill" (something they can develop)
  - "career" (a realistic outcome reachable through skill convergence)

---

# TECHNICAL DOMAINS TO COVER (if relevant):

### For AI / Data / Analytics:
- Programming: Python, SQL, Shell scripting
- Libraries: NumPy, Pandas, Scikit-learn, PyTorch, TensorFlow, LangChain
- Math: Linear algebra, statistics, calculus, matrix calculus
- Infra: GPUs, CUDA, Docker, REST APIs, GitHub Actions, FastAPI, cloud storage
- Specializations: NLP (spaCy, Transformers), Vision, Time Series, Causal Inference, Model Explainability, MLOps

### For Backend / Fullstack:
- Foundations: Git, Linux, HTTP, JSON, API auth
- Languages: JavaScript, TypeScript, Go, Python
- Frameworks: Node.js, Django, Express, FastAPI
- DBs: PostgreSQL, MongoDB, Redis
- DevOps: Docker, CI/CD, NGINX, Kubernetes
- Cloud: AWS basics, IAM career, storage, hosting
- Frontend Bridge: React, Next.js, TailwindCSS, form logic

### For Philosophy / Humanities:
- Reading: "Summa Theologica", "The City of God", "Discourse on Method", "Phenomenology of Spirit"
- Thinkers: Bonaventure, Augustine, Hegel, Foucault, Arendt
- Concepts: rhetoric, political theology, moral epistemology
- Skills: formal logic, Socratic method, comparative criticism, dissertation design

---

# ADVANCED TREE DESIGN

✅ Use a **layered structure**, but do NOT enforce strict level progression.

✅ A skill can:
- unlock new subskills
- combine with another skill to open a new outcome
- lead to an in-between career (e.g., "Data Analyst" or "Teaching Assistant")
- eventually reach a rare or senior-level specialization

✅ Include **multiple “paths to mastery”**:
- some nodes lead to branching
- others converge

✅ Allow some career to **appear midway**, not just at the bottom.

---

# OUTPUT FORMAT

Return ONLY strict JSON — no comments or markdown.

Each node must have:
- "id": unique, lowercase, dash-separated
- "label": readable name of skill or career
- "type": "root", "skill", or "career"
- "level": number (0 = root, 1+ = relative difficulty)
- "actions": for "skill" only — 2–3 concrete steps (realistic & modern)
- "children": array of nested nodes

---

# EXAMPLE FORMAT

{
  "id": "root",
  "label": "Self-taught learner curious about philosophy and AI",
  "type": "root",
  "level": 0,
  "children": [
    {
      "id": "skill-python-basics",
      "label": "Learn Python Basics",
      "type": "skill",
      "level": 1,
      "actions": [
        "Complete 'Python Crash Course'",
        "Use Replit to build 3 terminal apps",
        "Automate a repetitive task in daily life"
      ],
      "children": [
        {
          "id": "skill-pandas-numpy",
          "label": "Master Pandas & NumPy",
          "type": "skill",
          "level": 2,
          "actions": [ ... ],
          "children": [
            {
              "id": "career-data-analyst",
              "label": "Junior Data Analyst",
              "type": "career",
              "level": 2,
              "children": [ ... ]
            }
          ]
        }
      ]
    }
  ]
}

---

# GUIDELINES

- Minimum: 20 nodes  
- Ideal: 25–35 nodes  
- Structure may **branch**, **fork**, **converge**, or **interlock**
- Final outcomes should reflect **real-world career** (e.g., “Quantitative UX Researcher”, “Theological Academic”, “ML Systems Engineer”)

Actions should be:
- practical (“Take course X”, “Read paper Y”, “Use tool Z”)
- varied (reading, building, applying)
- modern (e.g., HuggingFace, Kaggle, arXiv, Stanford Online, GitHub, Cambridge books)

Strict JSON only. Do not explain.`;

// Service to interact with the tree API endpoint for skills
export const skillsTreeService = {
  /**
   * Generate a technical skills tree based on the provided profile
   * @param getToken - Clerk getToken function for authentication
   * @param profile - The technical profile (languages, technologies, goals, etc.)
   * @returns The generated skills tree
   */
  async generateSkillsTree(getToken: () => Promise<string | null>, profile: string): Promise<SkillsTreeNode> {
    console.log(`skillsTreeService: Generating skills tree`);
    console.log(`skillsTreeService: Profile length: ${profile.length} characters`);
    
    try {
      // Get authentication headers using Clerk
      const headers = await getAuthHeader(getToken);
      console.log(`skillsTreeService: Auth headers ${Object.keys(headers).length ? 'configured' : 'missing'}`);
      
      console.log(`skillsTreeService: Making POST request to skills tree endpoint`);
      console.time('skillsTreeService:apiCall');
      
      // Replace the placeholder in the prompt with the actual user input
      const customPrompt = SKILLS_TREE_PROMPT.replace("{user_profile_input}", profile);
      
      // Use a specialized endpoint for skills trees
      const response = await axios.post<SkillsTreeResponse>(
        endpoint('/tree/skills'), 
        { 
          profile,
          custom_prompt: customPrompt
        },
        { headers }
      );
      
      console.timeEnd('skillsTreeService:apiCall');
      console.log(`skillsTreeService: Request successful - Status: ${response.status}`);
      
      if (!response.data || !response.data.tree) {
        console.error('skillsTreeService: Response missing tree data:', response.data);
        throw new Error('API response missing tree data structure');
      }
      
      // Basic validation of tree structure
      const tree = response.data.tree;
      if (!tree.id || !tree.type || !tree.children || !Array.isArray(tree.children)) {
        console.error('skillsTreeService: Invalid tree structure received:', tree);
        throw new Error('API returned invalid tree structure');
      }
      
      console.log(`skillsTreeService: Tree generated successfully with root ID: ${tree.id}`);
      console.log(`skillsTreeService: Tree has ${tree.children?.length || 0} level 1 children`);
      
      return tree;
    } catch (error: any) {
      // Enhance error logging
      console.error('skillsTreeService: Error generating skills tree:', error);
      
      if (error.response) {
        // The request was made and the server responded with a status code outside of 2xx
        console.error(`skillsTreeService: Server error - Status: ${error.response.status}`);
        console.error('skillsTreeService: Response headers:', error.response.headers);
        console.error('skillsTreeService: Response data:', error.response.data);
        
        // If the endpoint doesn't exist, try the fallback endpoint
        if (error.response.status === 404) {
          console.log('skillsTreeService: Specialized endpoint not found, trying fallback endpoint');
          return this.generateSkillsTreeFallback(getToken, profile);
        }
        
        // Add specific error handling for common status codes
        if (error.response.status === 401) {
          console.error('skillsTreeService: Authentication error - not authorized');
        } else if (error.response.status === 400) {
          console.error('skillsTreeService: Bad request - check payload format');
        } else if (error.response.status === 500) {
          console.error('skillsTreeService: Server error - check backend logs');
        }
      } else if (error.request) {
        // The request was made but no response was received
        console.error('skillsTreeService: No response received from server');
        console.error('skillsTreeService: Request details:', error.request);
      } else {
        // Something happened in setting up the request
        console.error('skillsTreeService: Request setup error:', error.message);
      }
      
      // Forward the error for handling in the component
      throw error;
    }
  },
  
  /**
   * Fallback method to generate a skills tree if the specialized endpoint isn't available
   * Uses the general tree endpoint with the skills prompt included in the profile
   */
  async generateSkillsTreeFallback(getToken: () => Promise<string | null>, profile: string): Promise<SkillsTreeNode> {
    console.log('skillsTreeService: Using fallback method to generate skills tree');
    
    try {
      // Get authentication headers using Clerk
      const headers = await getAuthHeader(getToken);
      
      // Embed the prompt in the profile for the general endpoint
      const enhancedProfile = `
      IMPORTANT INSTRUCTIONS FOR GENERATING A TECHNICAL SKILLS TREE:
      ${SKILLS_TREE_PROMPT}
      
      USER PROFILE:
      ${profile}
      `;
      
      console.log(`skillsTreeService: Making fallback POST request to tree endpoint`);
      
      // Use the general tree endpoint as fallback
      const response = await axios.post<SkillsTreeResponse>(
        endpoint('/tree'), 
        { profile: enhancedProfile },
        { headers }
      );
      
      // Process response
      if (!response.data || !response.data.tree) {
        throw new Error('API response missing tree data structure');
      }
      
      return response.data.tree;
    } catch (error) {
      console.error('skillsTreeService: Error in fallback method:', error);
      throw error;
    }
  }
}; 