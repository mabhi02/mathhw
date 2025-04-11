# ABTS Unified Generator Frontend - Jobs To Be Done

This document outlines the development roadmap for the ABTS Unified Generator frontend and provides instructions for using the associated plan and state files to drive development.

## Development Roadmap

### Phase 1: Project Setup & Core UI Components
- Initialize Next.js with TypeScript
- Set up shadcn/ui components and Tailwind CSS
- Implement responsive layout with navigation
- Create design system based on ABTS color palette
- Set up API client utilities for backend communication

### Phase 2: Question Generation & Comparison
- Build question generation interface
- Create GPT-4o direct query interface
- Implement comparison view for A/B testing outputs
- Develop results display and management system

### Phase 3: Feedback System & Additional Features
- Create feedback collection system
- Build outline management interface
- Implement template system interface
- Develop dashboard with analytics

### Phase 4: Optimization & Finalization
- Implement long-running process handling
- Optimize performance
- Write tests and documentation
- Configure deployment and CI/CD

## Technology Stack
- Next.js with TypeScript
- shadcn/ui and Tailwind CSS
- React Query for state management
- Axios for API communication
- Zod for validation
- Jest and React Testing Library for testing

## Color Palette
- Primary: #1A5F7A (modernized ABTS blue)
- Secondary: #3A7CA5 (lighter blue accent)
- Accent: #D9A566 (warm gold accent)
- Background (Light): #F9FBFC / (Dark): #1A2330
- Text (Light): #2E3A48 / (Dark): #E9EDF1

## Using Plan and State Files for Development

The development of this frontend is driven by two key files:

1. `.build/.plans/abts_plan_frontend.md` - Contains the detailed implementation plan
2. `.build/.state/frontend_state.json` - Tracks the status of all tasks

### Development Workflow

1. **Start a New Task**:
   ```bash
   # View the current task structure and status
   cat .build/.plans/abts_plan_frontend.md
   cat .build/.state/frontend_state.json
   
   # Update the state to mark a task as in-progress
   .build/.tools/update_task.sh abts_plan_frontend in-progress "Starting Task 1.1: Frontend Framework Setup"
   ```

2. **Implement the Task**:
   - Work on the task as outlined in the plan
   - Refer to the plan for specific requirements and deliverables
   - Follow the existing project structure and conventions

3. **Complete the Task**:
   ```bash
   # Update the state to mark the task as done
   .build/.tools/update_task.sh abts_plan_frontend done "Completed Task 1.1: Frontend Framework Setup"
   
   # Validate the state against the plan
   .build/.tools/validate_state.py abts_plan_frontend
   ```

4. **Generate Progress Summary**:
   ```bash
   # Generate a summary of the current progress
   .build/.tools/generate_summary.sh week
   ```

### Task Prioritization

Follow the phases in order:
1. Complete all Phase 1 tasks before moving to Phase 2
2. Complete all Phase 2 tasks before moving to Phase 3
3. And so on...

Within each phase, tasks are ordered by importance. Start with Task X.1, then X.2, etc.

### Regular Checkpoints

- At the end of each week, generate a summary to track progress
- At the end of each phase, perform a comprehensive review
- Update the state file regularly to maintain accurate tracking

## Integration with Backend

The backend API is available at `http://localhost:8000/api` when running locally. Key endpoints include:

- `/api/questions/generate` - For generating questions
- `/api/feedback/` - For submitting feedback

Refer to the API documentation for detailed information about request/response formats and authentication requirements.

## Getting Started

1. Clone the repository
2. Install dependencies: `npm install` or `pnpm install`
3. Start the development server: `npm run dev` or `pnpm dev`
4. Access the application at `http://localhost:3000`

## Next Steps

The immediate next steps are:

1. Complete the Phase 1 setup tasks
2. Establish the core UI component library
3. Implement the responsive layout and navigation
4. Set up the API client for backend communication

Remember to update the state file as you progress through these tasks. 