"""This module contains the detection code for deprecated op codes."""
from mythril.analysis.potential_issues import (
    PotentialIssue,
    get_potential_issues_annotation,
)
from mythril.analysis.swc_data import DEPRECATED_FUNCTIONS_USAGE
from mythril.analysis.modules.base import DetectionModule
from mythril.laser.ethereum.state.global_state import GlobalState
import logging

log = logging.getLogger(__name__)

DESCRIPTION = """
Check for usage of deprecated opcodes
"""


class DeprecatedOperationsModule(DetectionModule):
    """This module checks for the usage of deprecated op codes."""

    def __init__(self):
        """"""
        super().__init__(
            name="Deprecated Operations",
            swc_id=DEPRECATED_FUNCTIONS_USAGE,
            description=DESCRIPTION,
            entrypoint="callback",
            pre_hooks=["ORIGIN", "CALLCODE"],
        )

    def _execute(self, state: GlobalState) -> None:
        """

        :param state:
        :return:
        """
        if state.get_current_instruction()["address"] in self.cache:
            return
        issues = self._analyze_state(state)

        annotation = get_potential_issues_annotation(state)
        annotation.potential_issues.extend(issues)

    def _analyze_state(self, state):
        """

        :param state:
        :return:
        """
        node = state.node
        instruction = state.get_current_instruction()

        if instruction["opcode"] == "ORIGIN":
            log.debug("ORIGIN in function " + node.function_name)
            title = "Use of tx.origin"
            description_head = "Use of tx.origin is deprecated."
            description_tail = (
                "The smart contract retrieves the transaction origin (tx.origin) using msg.origin. "
                "Use of msg.origin is deprecated and the instruction may be removed in the  future. "
                "Use msg.sender instead.\nSee also: "
                "https://solidity.readthedocs.io/en/develop/security-considerations.html#tx-origin"
            )
            swc_id = DEPRECATED_FUNCTIONS_USAGE

        elif instruction["opcode"] == "CALLCODE":
            log.debug("CALLCODE in function " + state.environment.active_function_name)
            title = "Use of callcode"
            description_head = "Use of callcode is deprecated."
            description_tail = (
                "The callcode method executes code of another contract in the context of the caller account. "
                "Due to a bug in the implementation it does not persist sender and value over the call. It was "
                "therefore deprecated and may be removed in the future. Use the delegatecall method instead."
            )
            swc_id = DEPRECATED_FUNCTIONS_USAGE
        else:
            return []

        potential_issue = PotentialIssue(
            contract=state.environment.active_account.contract_name,
            function_name=state.environment.active_function_name,
            address=instruction["address"],
            title=title,
            bytecode=state.environment.code.bytecode,
            detector=self,
            swc_id=swc_id,
            severity="Medium",
            description_head=description_head,
            description_tail=description_tail,
            constraints=[],
        )
        return [potential_issue]


detector = DeprecatedOperationsModule()
