class Node(object):
   def __init__(self, state, parent=None, choice_that_led_here=None):

        self.children = {}  # map from choice to node

        self.parent = parent
        self.state = state

        self.w = np.zeros(len(state.valid_actions))
        self.n = np.zeros(len(state.valid_actions))
        self.n += (1.0 + np.random.rand(len(self.n)))*1e-10
        self.prior_policy = 1.0/len(self.state.valid_actions)git

        self.sum_n = 1
        self.choice_that_led_here = choice_that_led_here

        self.move_number = 0

        if parent:
            self.move_number = parent.move_number + 1

    def history_sample(self):
        pi = np.zeros(self.state.action_space.n)
        pi[self.state.valid_actions] = self.n/self.n.sum()
        return [self.state, self.state.observed_state(), pi]

    def add_noise_to_prior(self, noise_frac=0.25, dirichlet_alpha=0.03):
        noise = np.random.dirichlet(
            dirichlet_alpha*np.ones(len(self.state.valid_actions)))
        self.prior_policy = (1-noise_frac)*self.prior_policy + noise_frac*noise
