import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv

class GraphSAGE(torch.nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim, dropout=0.2):
        super().__init__()
        self.conv1 = SAGEConv(input_dim, hidden_dim)
        self.norm1 = nn.BatchNorm1d(hidden_dim)
        self.conv2 = SAGEConv(hidden_dim, output_dim)
        self.dropout = dropout

    def forward(self, x, edge_index, edge_type=None):
        x = self.conv1(x, edge_index)
        x = self.norm1(x)
        x = F.relu(x)
        x = F.dropout(x, p=self.dropout, training=self.training)
        x = self.conv2(x, edge_index)
        return x

class EdgeRegHead(torch.nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.mlp = torch.nn.Sequential(
            torch.nn.Linear(dim * 2, dim),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.2),
            torch.nn.Linear(dim, dim // 2),
            torch.nn.ReLU(),
            torch.nn.Linear(dim // 2, 1),
            torch.nn.Sigmoid()
        )

    def forward(self, zi, zj):
        return self.mlp(torch.cat([zi, zj], dim=-1))

class CareerTreeModel(torch.nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim, num_relations=None, dropout=0.2):
        super().__init__()
        self.encoder = GraphSAGE(input_dim, hidden_dim, output_dim, dropout)
        self.edge_reg = EdgeRegHead(output_dim)

    def forward(self, x, edge_index, edge_type=None, edge_pairs=None):
        node_embeddings = self.encoder(x, edge_index)

        if edge_pairs is not None:
            zi = node_embeddings[edge_pairs[0]]
            zj = node_embeddings[edge_pairs[1]]
            edge_scores = self.edge_reg(zi, zj)
            return edge_scores

        return node_embeddings

    def get_node_embeddings(self, x, edge_index, edge_type=None):
        return self.encoder(x, edge_index)
