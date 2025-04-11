/**
 *
 **/
Ext._define('core.TreeMoveWindow', {
    'extend': 'core.TreeActionWindow',

    'moveTo': function(to) {
        var params = {};

        params[this.folderIndexField] = to.id;
        Ext._create(
            this.restWindow
        ).factoryRestful().update(
            this.selected.id,
            {
                'params': params,
                'scope': this,
                'externalCallback': {
                    'success': {
                        'scope': this,
                        'fn': function() {
                            this.destroy();
                            core.invokeCallback(this.callback.success, to);
                        }
                    }
                }
            },
            {
                'el': this.getEl(),
                'message': 'Movendo item selecionado...'
            }
        );
    },

    'getActionButton': function() {
        if(!this._actionButton)
            this._actionButton = Ext._create('Ext.Button', {
                'text': 'Mover',
                'scope': this,
                'handler': function() {
                    var to = this.getTreePanel().getSelectionModel().getSelectedNode();
                    this.moveTo(to);
                }
            });

        return this._actionButton;
    }
})