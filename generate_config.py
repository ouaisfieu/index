#!/usr/bin/env python3
"""
Script de génération automatique du fichier config.json pour le système de gestion de notes.

Ce script parcourt le répertoire `notes/` et cherche dans chaque fichier Markdown
des métadonnées au format YAML en début de fichier (entre des lignes '---').
Ces métadonnées doivent définir au minimum un identifiant (`id`) et un titre (`title`),
mais peuvent également inclure des tags (`tags`) et des liens (`links`).

Exemple de front‑matter YAML dans un fichier Markdown :

    ---
    id: machine-learning
    title: Machine Learning
    tags:
      - IA
      - Algorithmes
    links:
      - ai-general
      - neural-networks
    ---
    # Contenu du fichier…

Le script produit un fichier `config.json` compatible avec l’application web.
Chaque entrée contient l’identifiant de la note, le titre, la liste des tags,
le chemin du fichier Markdown et la liste des identifiants des notes liées.

Pour exécuter le script :

    python generate_config.py

Le fichier `config.json` sera écrit dans le répertoire courant.
"""

import os
import json
from typing import List, Dict

import yaml  # Utilisé pour parser le front‑matter YAML


def parse_markdown_front_matter(content: str) -> Dict:
    """Extrait et parse le front‑matter YAML d’un fichier Markdown.

    Si le fichier commence par '---', on considère le contenu jusqu’au prochain '---'
    comme front‑matter. On renvoie un dictionnaire des métadonnées.
    En cas d’absence de front‑matter ou d’erreur de parsing, renvoie un dictionnaire vide.
    """
    if not content.startswith('---'):
        return {}
    try:
        # Séparation en trois parties : '', front‑matter, reste du document
        parts = content.split('---', 2)
        if len(parts) < 3:
            return {}
        _, fm_text, _ = parts
        meta = yaml.safe_load(fm_text)
        return meta if isinstance(meta, dict) else {}
    except Exception:
        return {}


def build_config_from_notes(notes_dir: str) -> Dict[str, List[Dict]]:
    """Construit la structure de configuration à partir des fichiers Markdown.

    Parcourt les fichiers .md du répertoire `notes_dir`, lit le front‑matter YAML
    et construit une liste de dictionnaires au format attendu par l’application.
    """
    notes = []
    for filename in sorted(os.listdir(notes_dir)):
        if not filename.lower().endswith('.md'):
            continue
        path = os.path.join(notes_dir, filename)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        meta = parse_markdown_front_matter(content)
        # Déterminer les champs en se basant sur le front‑matter ou sur le nom de fichier
        id_ = meta.get('id') if isinstance(meta.get('id'), str) else os.path.splitext(filename)[0]
        title = meta.get('title') if isinstance(meta.get('title'), str) else id_
        tags = meta.get('tags') if isinstance(meta.get('tags'), list) else []
        links = meta.get('links') if isinstance(meta.get('links'), list) else []

        notes.append({
            "id": id_,
            "title": title,
            "tags": tags,
            # le chemin du fichier relatif à la racine du projet
            "file": os.path.join(notes_dir, filename).replace('\\', '/'),
            "links": links
        })

    return {"notes": notes}


def main():
    notes_dir = 'notes'
    if not os.path.isdir(notes_dir):
        raise SystemExit(f"Le répertoire '{notes_dir}' n'existe pas. Crééz‑le et ajoutez des fichiers Markdown.")

    config = build_config_from_notes(notes_dir)
    # Écriture de config.json à la racine du projet
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"Fichier config.json généré avec {len(config['notes'])} notes.")


if __name__ == '__main__':
    main()