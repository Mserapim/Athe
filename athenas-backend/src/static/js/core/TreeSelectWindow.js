/**
 *
 **/
Ext._define('core.TreeSelectWindow', {
    'extend': 'core.TreeActionWindow',

    'getActionButton': function() {
        if(!this._actionButton)
            this._actionButton = Ext._create('Ext.Button', {
                'text': 'Selecionar',
                'scope': this,
                'handler': function() {
                    var selected = this.getTreePanel().getSelectionModel().getSelectedNode();
                    core.invokeCallback(this.callback, selected);
                    this.destroy();
                }
            });

        return this._actionButton;
    }
})