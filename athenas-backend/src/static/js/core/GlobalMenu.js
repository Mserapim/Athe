/**
 *
 **/
Ext._define('core.GlobalMenu', {
    'extend': 'Ext.Window',

    'toogleMenu': function() {
        this.setVisible(!this.isVisible());
    },

    'constructor': function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            'width': 100,
            'height': 100,
            'frame': false
        });

        Ext.apply(
            cfg,
            {
                'closable': false,
                'autoShow': true,
                'showAnimDuration': 0.1,
                'hideAnimDuration': 0.1
            }
        );

        // this.callParent([cfg]);
        core.GlobalMenu.superclass.constructor.call(this, cfg);
    }
});
