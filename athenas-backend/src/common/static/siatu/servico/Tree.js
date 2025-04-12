/**
 *
 **/
Ext._define('common.siatu.servico.Tree', {
    extend: 'core.RestfulTree',

    restWindow: 'common.siatu.servico.Window',

    folderIndexField: 'servico_superior',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        common.siatu.servico.Tree.superclass.constructor.call(this, cfg);

        this.on({
            scope: this,
            load: function(node) {
                if (node.id == 0){
                    Ext.each(
                        node.childNodes,
                        function(childNode) {
                            childNode.expand()
                        },
                        this
                    );
                }
            },
        })
    }
})
