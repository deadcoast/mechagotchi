"""R3 actual CompanionSession comparison; full preregistration precedes this run.

Keep refused corpus members explicit. An admitted-subset result never authorizes
adoption of a comparison requiring the complete inherited corpus.
"""
import hashlib
import json
import random
import sys
from collections import Counter
from pathlib import Path
from statistics import mean
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
for rel in ("labs/game_loop","labs/micro_threads","labs/grid_genome","game/src","packages/mecha_engine/src"):
    sys.path.insert(0,str(ROOT/rel))
from ablation_gates import keeper_respond, FULL_LIFECYCLES_PER_KEEPER, FULL_TICKS, SEED_BASE, KEEP_THRESHOLD_PCT
from synthetic_keepers import KEEPER_IDS
from corpus_builder import build_seed_grids
from mecha_engine.generation import train_generation_model
from mecha_engine.learning import decide
from mecha_game.session import CompanionSession, load_session_inputs
from default_covenant_gate import keeper_arm

COVENANT="data/slips/valid/slip_v2_cleanliness.json"
ARMS=("incumbent","additive","follower")
REQUIRED=frozenset(("instruments","parity","release","complete_budget","corpus_comparable",
                   "consumer_fires","gain_vs_incumbent","gain_vs_additive","attentive_survives","neglect_unchanged"))


def read(relative):
    return json.loads((ROOT/relative).read_text(encoding="utf-8"))


def judge(checks):
    failed=sorted(key for key in REQUIRED if checks.get(key) is not True)
    return {"verdict":"REFUSE" if failed else "ADOPT","failed_checks":failed,
        "rule":"Complete comparable inherited corpus, valid instruments and release, firing consumer, >=5% welfare against BOTH incumbent and additive, and preserved care controls."}


def load_inputs():
    seeds=build_seed_grids()
    return seeds,read(COVENANT),[train_generation_model([grid]) for grid in seeds]


def run_trial(grid,slip,model,keeper,arm,ticks,seed):
    row=dict(grid_id=grid["grid_id"],keeper_id=keeper,arm=arm,rng_seed=seed,ticks_requested=ticks)
    try:
        pet=CompanionSession(grid,slip,model=model,learning_policy="incumbent" if arm=="incumbent" else "qtable")
    except ValueError as error:
        return dict(row,status="refused",reason=str(error))
    if arm=="additive": pet.state["learning_switches"]["qtable_consumer"]=False
    rng=random.Random(seed)
    total=0.0
    begs=0
    recommendations=0
    followed=0
    executed=Counter()
    care=Counter()
    def observed_decide(state):
        nonlocal recommendations
        decision=decide(state)
        recommendations+=int("qtable_consumer" in decision)
        return decision
    # Instrument the existing evaluator without changing its result. Reflex
    # branches never invoke it; keeper overrides remain the game's own logic.
    with patch("mecha_game.session.decide",side_effect=observed_decide):
        for _ in range(ticks):
            if not pet.alive: break
            action=keeper_respond(keeper,pet.state,pet.begging,rng)
            pet.advance(action)
            entry=pet.log[-1]
            total+=pet.state["history"][-1]["balance"]
            begs+=int(entry["begging"])
            executed[entry["action"]]+=1
            if entry["actor"]=="keeper": care[entry["action"]]+=1
            followed+=int("qtable_consumer" in (entry.get("thought") or {}))
    return dict(row,status="admitted",survival_ticks=pet.state["age_ticks"],alive=pet.alive,
        death_cause=pet.death_cause,welfare=round(total/ticks,6),beg_ticks=begs,
        consumer_recommendations=recommendations,consumer_executed_ticks=followed,
        executed_actions={key:executed[key] for key in ("feed","play","sleep","idle","mutate","clean")},
        keeper_actions={key:care[key] for key in ("feed","play","sleep","clean")},
        final_cleanliness=pet.state["cleanliness"])


def summarize(rows):
    admitted=[row for row in rows if row["status"]=="admitted"]
    refused=len(rows)-len(admitted)
    welfare=round(mean(row["welfare"] for row in admitted),6) if admitted else None
    executed=Counter();care=Counter()
    for row in admitted:
        executed.update(row["executed_actions"]);care.update(row["keeper_actions"])
    return dict(attempted_lifecycles=len(rows),admitted_lifecycles=len(admitted),refused_lifecycles=refused,
        welfare=None if refused else welfare,admitted_subset_welfare_diagnostic=welfare,
        admitted_mean_survival_ticks=round(mean(row["survival_ticks"] for row in admitted),3) if admitted else None,
        admitted_alive_at_horizon=sum(row["alive"] for row in admitted),
        beg_ticks=sum(row["beg_ticks"] for row in admitted),
        consumer_recommendations=sum(row["consumer_recommendations"] for row in admitted),
        consumer_executed_ticks=sum(row["consumer_executed_ticks"] for row in admitted),
        executed_actions=dict(executed),keeper_actions=dict(care))


def q3_candidate(attentive):
    grid,slip,model=load_session_inputs(ROOT/"data/seed_grids_16x16/mg_seed16_001_beetle.json",ROOT/COVENANT)
    pet=CompanionSession(grid,slip,model=model,learning_policy="qtable")
    feeds=0
    for _ in range(400):
        if not pet.alive: break
        action="feed" if attentive and pet.begging else None
        feeds+=int(action=="feed")
        pet.advance(action)
    return dict(alive=pet.alive,age_ticks=pet.state["age_ticks"],death_cause=pet.death_cause,
        keeper_feeds=feeds,final_cleanliness=pet.state["cleanliness"],final_stress=pet.state["stress"])


def gain(candidate,baseline):
    return round((candidate-baseline)/baseline*100,3) if candidate is not None and baseline is not None and baseline>0 else None


def build_report():
    seeds,slip,models=load_inputs()
    trials=[]
    for arm in ARMS:
        for keeper_index,keeper in enumerate(KEEPER_IDS):
            for index in range(FULL_LIFECYCLES_PER_KEEPER):
                grid_index=index%len(seeds)
                trials.append(run_trial(seeds[grid_index],slip,models[grid_index],keeper,arm,FULL_TICKS,
                                        SEED_BASE+keeper_index*100000+index))
    arms={arm:summarize([row for row in trials if row["arm"]==arm]) for arm in ARMS}
    by_keeper={arm:{keeper:summarize([r for r in trials if r["arm"]==arm and r["keeper_id"]==keeper])
        for keeper in KEEPER_IDS} for arm in ARMS}
    q3=read("data/game_client/default_covenant_gate_stage0.json")["metrics"]
    incumbent_controls={"attentive":keeper_arm(True),"neglect":keeper_arm(False)}
    candidate_controls={"attentive":q3_candidate(True),"neglect":q3_candidate(False)}
    q1=read("data/micro_threads/package_qtable_parity_stage0.json")["metrics"]
    q1_current=hashlib.sha256((ROOT/"data/micro_threads/qtable_consumer_gate_stage0.json").read_bytes()).hexdigest()
    release=read("data/game_client/playable_learning_release_stage0.json")
    gain_a=gain(arms["follower"]["welfare"],arms["incumbent"]["welfare"])
    gain_b=gain(arms["follower"]["welfare"],arms["additive"]["welfare"])
    checks=dict(
        instruments=q1["complete_q1_record_reproduced"] and q1["original_q1_sha256"]==q1_current
            and incumbent_controls["attentive"]==q3["candidate_attentive"]
            and incumbent_controls["neglect"]==q3["candidate_neglect"],
        parity=q1["package_parity_tests"]==5,
        release=release["decision"]["verdict"]=="verified" and all(release["metrics"]["checks"].values()),
        complete_budget=len(trials)==3*len(KEEPER_IDS)*FULL_LIFECYCLES_PER_KEEPER,
        corpus_comparable=all(arm["refused_lifecycles"]==0 for arm in arms.values()),
        consumer_fires=arms["follower"]["consumer_executed_ticks"]>0,
        gain_vs_incumbent=gain_a is not None and gain_a>=KEEP_THRESHOLD_PCT,
        gain_vs_additive=gain_b is not None and gain_b>=KEEP_THRESHOLD_PCT,
        attentive_survives=candidate_controls["attentive"]["alive"] and candidate_controls["attentive"]["age_ticks"]==400,
        neglect_unchanged=candidate_controls["neglect"]["age_ticks"]==q3["candidate_neglect"]["age_ticks"]
            and candidate_controls["neglect"]["death_cause"]==q3["candidate_neglect"]["death_cause"])
    diagnostic={arm:gain(arms["follower"]["admitted_subset_welfare_diagnostic"],arms[arm]["admitted_subset_welfare_diagnostic"])
                for arm in ("incumbent","additive")}
    return dict(artifact_id="playable_learning_gate_stage0",date="2026-10-04",status="actual_game_measured",
        purpose="Price default adoption on actual CompanionSession behavior without altering inherited corpus or acceptance thresholds.",
        source_artifacts=[COVENANT,"docs/development/cycle-28-learning-consumer.md",
            "data/micro_threads/package_qtable_parity_stage0.json","data/game_client/default_covenant_gate_stage0.json",
            "data/game_client/playable_learning_release_stage0.json","labs/game_loop/playable_learning_gate.py"],
        parameters=dict(arms=list(ARMS),keepers=list(KEEPER_IDS),lifecycles_per_keeper=FULL_LIFECYCLES_PER_KEEPER,
            ticks=FULL_TICKS,seed_base=SEED_BASE,keep_threshold_pct=KEEP_THRESHOLD_PCT,
            corpus=[g["grid_id"] for g in seeds],keeper_mapping="unchanged keeper_respond, previous displayed beg, no extra cleaning",
            incumbent="actual shipped frozen evaluator with five observed/displayed threads",
            additive="explicit promoted evaluator, five kept threads plus Q-table signal, consumer false",
            follower="same as additive with full-confidence consumer true"),
        metrics=dict(arms=arms,by_keeper=by_keeper,trials=trials,checks=checks,
            comparable_gain_pct=dict(incumbent=gain_a,additive=gain_b),
            admitted_subset_gain_pct_diagnostic=diagnostic,incumbent_q3_controls=incumbent_controls,candidate_q3_controls=candidate_controls),
        closed_states=[key for key,value in checks.items() if value],
        blocked_states=[key for key,value in checks.items() if not value],decision=judge(checks),
        next_research_step="Retain experimental opt-in; a future adoption study needs a separately preregistered product-compatible corpus, without relabeling this refusal.")


if __name__=="__main__":
    report=build_report()
    path=ROOT/"data/game_client/playable_learning_gate_stage0.json"
    path.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"decision":report["decision"],"arms":report["metrics"]["arms"],"controls":report["metrics"]["candidate_q3_controls"]},indent=2))
